## 视频系统SDK集成
本项目是用于集成不同监控设备厂家的`SDK`， 目前包括海康、大华。 实现思路是通过后台管理系统的`HTTP API`方式集成。

### 数据结构示例

```json
{
    "address" : {
        "ip" : "192.0.0.18",
        "port" : 80
    },
    "user" : "admin",
    "password" : "admin",
    "type" : "hikvision",
    "deviceName" : "Embedded Net DVR",
    "model" : "DS-7816H-SNH",
    "serialNumber" : "DS-7816H-SNH1620140125AACH450813722WCVU",
    "deviceType" : "DVR",
    "protocol" : {
        "name" : "rtsp",
        "port" : 554 
    },
    "channels" : [ 
        {
            "name" : "Camera 01",
            "inputPort" : 1,
            "online": true,
            "mainStream" : {
                "videoEnable" : true,
                "vcodec" : "H.264",
                "audioEnable" : true,
                "acodec" : "G.711ulaw"
            },
            "subStream" : {
                "videoEnable" : true,
                "vcodec" : "H.264",
                "audioEnable" : true,
                "acodec" : "G.711ulaw"
            }
        }
    ]
}
```

### 已验证设备的型号

**海康NVR**：`DS-8832N-K8`   `DS-7816N-K2`  
**海康DVR**：`DS-7804HW-E1/M` `DS-7816H-SNH`  
**海康IPC**： `DS-7804N-SN`  `DS-2CD40653DEF-T`  
**海康IPD**： `DS-2DF5284-A`  `DS-2DE7235DI-A`  

**大华NVR**：`DH-NVR4832-4KS2`  
**大华DVR**：  
**大华IPC**：`IPC-HFW1105B`  
**大华IPD**： `DH-SD-6A1230S-HN`