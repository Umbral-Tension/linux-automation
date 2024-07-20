import json




platform = { 
    "os_list":{
        "debian":{
            "pm": "apt",
            "install_cmd":"sudo apt -y install",
            "uninstall_cmd":"sudo apt -y remove",
            "update":"apt update && sudo /usr/bin/apt -y upgrade",
        },
        "ubuntu":{
            "pm": "apt",
            "install_cmd":"sudo apt -y install ",
            "uninstall_cmd":"sudo apt -y remove ",
            "update":"apt update && sudo /usr/bin/apt -y upgrade",
        },
        "mint":{
            "pm": "apt",
            "install_cmd":"sudo apt -y install ",
            "uninstall_cmd":"sudo apt -y remove ",
            "update":"apt update && sudo /usr/bin/apt -y upgrade",
        },
        "fedora":{
            "pm": "dnf",
            "install_cmd":"sudo dnf -y install ",
            "uninstall_cmd":"sudo dnf -y remove ",
            "update":"sudo dnf upgrade"
        },
        
    },
}

with open('platform_info.json', 'w') as f:
    json.dump(platform, f, indent=2)
    
     