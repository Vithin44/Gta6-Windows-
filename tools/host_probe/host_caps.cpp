// Read-only CPU and D3D12 capability probe.
// It does not open game files, create a game process, submit GPU work, or change settings.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <dxgi1_2.h>
#include <d3d12.h>
#include <wrl/client.h>
#include <intrin.h>

#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#pragma comment(lib, "dxgi.lib")
#pragma comment(lib, "d3d12.lib")

using Microsoft::WRL::ComPtr;

static std::string json_escape(const std::string& value) {
    std::string out;
    out.reserve(value.size() + 8);
    for (unsigned char c : value) {
        switch (c) {
        case '"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20) {
                const char hex[] = "0123456789abcdef";
                out += "\\u00";
                out += hex[(c >> 4) & 0xf];
                out += hex[c & 0xf];
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    return out;
}

static std::string utf8(const wchar_t* value) {
    if (!value || !*value) return {};
    const int needed = WideCharToMultiByte(CP_UTF8, 0, value, -1, nullptr, 0, nullptr, nullptr);
    if (needed <= 1) return {};
    std::string out(static_cast<size_t>(needed), '\0');
    WideCharToMultiByte(CP_UTF8, 0, value, -1, out.data(), needed, nullptr, nullptr);
    out.pop_back();
    return out;
}

struct CpuInfo {
    std::string vendor;
    std::string brand;
    bool avx = false;
    bool avx2_hardware = false;
    bool avx2_os_enabled = false;
    bool sse4a = false;
    bool clwb = false;
    bool clzero = false;
    bool monitorx = false;
    bool mwaitx = false;
    bool clflushopt = false;
    bool fma3 = false;
    bool bmi1 = false;
    bool bmi2 = false;
};

static CpuInfo query_cpu() {
    CpuInfo info;
    int r[4] = {};
    __cpuid(r, 0);
    const int max_basic = r[0];
    char vendor[13] = {};
    std::memcpy(vendor + 0, &r[1], 4); // EBX
    std::memcpy(vendor + 4, &r[3], 4); // EDX
    std::memcpy(vendor + 8, &r[2], 4); // ECX
    info.vendor = vendor;

    if (max_basic >= 1) {
        __cpuidex(r, 1, 0);
        info.avx = (r[2] & (1 << 28)) != 0;
        info.fma3 = (r[2] & (1 << 12)) != 0;
        const bool osxsave = (r[2] & (1 << 27)) != 0;
        if (info.avx && osxsave) {
            const unsigned __int64 xcr0 = _xgetbv(0);
            info.avx2_os_enabled = (xcr0 & 0x6) == 0x6;
        }
    }

    if (max_basic >= 7) {
        __cpuidex(r, 7, 0);
        info.bmi1 = (r[1] & (1 << 3)) != 0;
        info.avx2_hardware = (r[1] & (1 << 5)) != 0;
        info.bmi2 = (r[1] & (1 << 8)) != 0;
        info.clflushopt = (r[1] & (1 << 23)) != 0;
        info.clwb = (r[1] & (1 << 24)) != 0;
    }

    __cpuid(r, 0x80000000);
    const unsigned int max_extended = static_cast<unsigned int>(r[0]);
    if (max_extended >= 0x80000001) {
        __cpuid(r, 0x80000001);
        info.sse4a = (r[2] & (1 << 6)) != 0;
        info.monitorx = (r[2] & (1 << 29)) != 0;
        info.mwaitx = info.monitorx;
    }
    if (max_extended >= 0x80000002) {
        char brand[49] = {};
        for (unsigned int leaf = 0; leaf < 3; ++leaf) {
            __cpuid(r, static_cast<int>(0x80000002 + leaf));
            std::memcpy(brand + leaf * 16, r, 16);
        }
        info.brand = brand;
    }
    if (max_extended >= 0x80000008) {
        __cpuid(r, 0x80000008);
        info.clzero = (r[1] & 1) != 0;
    }
    return info;
}

static const char* feature_level_name(D3D_FEATURE_LEVEL level) {
    switch (level) {
    case D3D_FEATURE_LEVEL_12_2: return "12_2";
    case D3D_FEATURE_LEVEL_12_1: return "12_1";
    case D3D_FEATURE_LEVEL_12_0: return "12_0";
    case D3D_FEATURE_LEVEL_11_1: return "11_1";
    case D3D_FEATURE_LEVEL_11_0: return "11_0";
    default: return "unknown";
    }
}

static const char* mesh_tier_name(D3D12_MESH_SHADER_TIER tier) {
    switch (tier) {
    case D3D12_MESH_SHADER_TIER_NOT_SUPPORTED: return "not_supported";
    case D3D12_MESH_SHADER_TIER_1: return "1";
    default: return "unknown";
    }
}

static std::string shader_model_name(D3D_SHADER_MODEL model) {
    const unsigned int value = static_cast<unsigned int>(model);
    const unsigned int major = (value >> 4) & 0xf;
    const unsigned int minor = value & 0xf;
    return std::to_string(major) + "_" + std::to_string(minor);
}

struct AdapterResult {
    std::string name;
    unsigned int vendor_id = 0;
    unsigned int device_id = 0;
    unsigned long long dedicated_video_memory = 0;
    bool d3d12_available = false;
    std::string feature_level = "unavailable";
    std::string shader_model = "unavailable";
    bool wave_ops = false;
    unsigned int wave_lane_min = 0;
    unsigned int wave_lane_max = 0;
    std::string mesh_shader_tier = "not_queried";
    long d3d12_create_hr = 0;
    long shader_model_hr = 0;
    long options1_hr = 0;
    long options7_hr = 0;
};

static AdapterResult query_adapter(IDXGIAdapter1* adapter) {
    AdapterResult result;
    DXGI_ADAPTER_DESC1 desc = {};
    if (FAILED(adapter->GetDesc1(&desc))) return result;

    result.name = utf8(desc.Description);
    result.vendor_id = desc.VendorId;
    result.device_id = desc.DeviceId;
    result.dedicated_video_memory = static_cast<unsigned long long>(desc.DedicatedVideoMemory);

    ComPtr<ID3D12Device> device;
    const D3D_FEATURE_LEVEL levels[] = {
        D3D_FEATURE_LEVEL_12_2,
        D3D_FEATURE_LEVEL_12_1,
        D3D_FEATURE_LEVEL_12_0,
        D3D_FEATURE_LEVEL_11_1,
        D3D_FEATURE_LEVEL_11_0
    };
    HRESULT hr = E_FAIL;
    for (D3D_FEATURE_LEVEL level : levels) {
        hr = D3D12CreateDevice(adapter, level, IID_PPV_ARGS(&device));
        if (SUCCEEDED(hr)) {
            result.d3d12_available = true;
            result.feature_level = feature_level_name(level);
            break;
        }
    }
    result.d3d12_create_hr = static_cast<long>(hr);
    if (!result.d3d12_available) return result;

    const D3D_SHADER_MODEL candidates[] = {
        D3D_SHADER_MODEL_6_7,
        D3D_SHADER_MODEL_6_6,
        D3D_SHADER_MODEL_6_5,
        D3D_SHADER_MODEL_6_4,
        D3D_SHADER_MODEL_6_3,
        D3D_SHADER_MODEL_6_2,
        D3D_SHADER_MODEL_6_1,
        D3D_SHADER_MODEL_6_0
    };
    for (D3D_SHADER_MODEL candidate : candidates) {
        D3D12_FEATURE_DATA_SHADER_MODEL data = {};
        data.HighestShaderModel = candidate;
        hr = device->CheckFeatureSupport(
            D3D12_FEATURE_SHADER_MODEL,
            &data,
            sizeof(data)
        );
        if (SUCCEEDED(hr)) {
            result.shader_model = shader_model_name(data.HighestShaderModel);
            result.shader_model_hr = static_cast<long>(hr);
            break;
        }
        result.shader_model_hr = static_cast<long>(hr);
    }

    D3D12_FEATURE_DATA_D3D12_OPTIONS1 options1 = {};
    hr = device->CheckFeatureSupport(
        D3D12_FEATURE_D3D12_OPTIONS1,
        &options1,
        sizeof(options1)
    );
    result.options1_hr = static_cast<long>(hr);
    if (SUCCEEDED(hr)) {
        result.wave_ops = options1.WaveOps != FALSE;
        result.wave_lane_min = options1.WaveLaneCountMin;
        result.wave_lane_max = options1.WaveLaneCountMax;
    }

    D3D12_FEATURE_DATA_D3D12_OPTIONS7 options7 = {};
    hr = device->CheckFeatureSupport(
        D3D12_FEATURE_D3D12_OPTIONS7,
        &options7,
        sizeof(options7)
    );
    result.options7_hr = static_cast<long>(hr);
    if (SUCCEEDED(hr)) {
        result.mesh_shader_tier = mesh_tier_name(options7.MeshShaderTier);
    }
    return result;
}

int main() {
    const CpuInfo cpu = query_cpu();

    std::vector<AdapterResult> adapters;
    ComPtr<IDXGIFactory1> factory;
    const HRESULT factory_hr = CreateDXGIFactory1(IID_PPV_ARGS(&factory));
    if (SUCCEEDED(factory_hr)) {
        for (UINT index = 0;; ++index) {
            ComPtr<IDXGIAdapter1> adapter;
            const HRESULT enum_hr = factory->EnumAdapters1(index, &adapter);
            if (enum_hr == DXGI_ERROR_NOT_FOUND) break;
            if (FAILED(enum_hr)) continue;

            DXGI_ADAPTER_DESC1 desc = {};
            if (FAILED(adapter->GetDesc1(&desc))) continue;
            if ((desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE) != 0) continue;
            adapters.push_back(query_adapter(adapter.Get()));
        }
    }

    std::cout
        << "{\n"
        << "  \"probe_version\": 1,\n"
        << "  \"cpu\": {\n"
        << "    \"vendor\": \"" << json_escape(cpu.vendor) << "\",\n"
        << "    \"brand\": \"" << json_escape(cpu.brand) << "\",\n"
        << "    \"avx\": " << (cpu.avx ? "true" : "false") << ",\n"
        << "    \"avx2_hardware\": " << (cpu.avx2_hardware ? "true" : "false") << ",\n"
        << "    \"avx2_os_enabled\": " << (cpu.avx2_os_enabled ? "true" : "false") << ",\n"
        << "    \"sse4a\": " << (cpu.sse4a ? "true" : "false") << ",\n"
        << "    \"clwb\": " << (cpu.clwb ? "true" : "false") << ",\n"
        << "    \"clzero\": " << (cpu.clzero ? "true" : "false") << ",\n"
        << "    \"monitorx\": " << (cpu.monitorx ? "true" : "false") << ",\n"
        << "    \"mwaitx\": " << (cpu.mwaitx ? "true" : "false") << ",\n"
        << "    \"clflushopt\": " << (cpu.clflushopt ? "true" : "false") << ",\n"
        << "    \"fma3\": " << (cpu.fma3 ? "true" : "false") << ",\n"
        << "    \"bmi1\": " << (cpu.bmi1 ? "true" : "false") << ",\n"
        << "    \"bmi2\": " << (cpu.bmi2 ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"dxgi_factory_available\": " << (SUCCEEDED(factory_hr) ? "true" : "false") << ",\n"
        << "  \"adapters\": [";

    for (size_t i = 0; i < adapters.size(); ++i) {
        const auto& a = adapters[i];
        if (i) std::cout << ",";
        std::cout
            << "\n    {"
            << "\"name\": \"" << json_escape(a.name) << "\","
            << "\"vendor_id\": " << a.vendor_id << ","
            << "\"device_id\": " << a.device_id << ","
            << "\"dedicated_video_memory_bytes\": " << a.dedicated_video_memory << ","
            << "\"d3d12_available\": " << (a.d3d12_available ? "true" : "false") << ","
            << "\"feature_level\": \"" << a.feature_level << "\","
            << "\"shader_model\": \"" << a.shader_model << "\","
            << "\"wave_ops\": " << (a.wave_ops ? "true" : "false") << ","
            << "\"wave_lane_min\": " << a.wave_lane_min << ","
            << "\"wave_lane_max\": " << a.wave_lane_max << ","
            << "\"mesh_shader_tier\": \"" << a.mesh_shader_tier << "\","
            << "\"d3d12_create_hr\": " << a.d3d12_create_hr << ","
            << "\"shader_model_hr\": " << a.shader_model_hr << ","
            << "\"options1_hr\": " << a.options1_hr << ","
            << "\"options7_hr\": " << a.options7_hr
            << "}";
    }
    if (!adapters.empty()) std::cout << "\n  ";
    std::cout << "]\n}\n";
    return 0;
}
