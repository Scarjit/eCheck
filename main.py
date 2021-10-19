import subprocess
import requests
from joblib import Parallel, delayed

from esearch import e_search_result_from_dict


def check_package(package_name: str) -> (int, str, str):
    package_name = package_name.replace("package:", "")
    result = requests.get(
        f"https://api.cleanapk.org/v2/apps?action=search&keyword={package_name}&nres=6&page=1&type=any&source=any")

    if result.status_code != 200:
        print(f"Failed to lookup {package_name}\n")
        return False, package_name, "FAILED TO LOOKUP !"

    if "com.android" in package_name or "com.google.android" in package_name or "org.lineageos" in package_name:
        return 2, package_name, ""
    e_res = e_search_result_from_dict(result.json())

    if e_res.success:
        for app in e_res.apps:
            if app.package_name == package_name:
                return 0, app.package_name, app.name
        return 1, package_name, ""


def main():
    devices: list[str] = subprocess.check_output("adb devices -l", shell=True).decode("UTF-8").strip().splitlines()[1:]
    if len(devices) > 1:
        print("Found more then one device, please disconnect all except one !")
        return
    elif len(devices) == 0:
        print("No device found, make sure to enable ADB")
        return

    devicex = list(filter(len, devices[0].split(" ")))

    device_name = ""
    for device in devicex:
        if "device:" in device:
            device_name = device.replace("device:", "")

    found_list = []
    missing_list = []
    skip_list = []

    packages_str: str = subprocess.check_output("adb shell 'pm list packages'", shell=True).decode("UTF-8")
    packages = packages_str.splitlines()
    print(f"Checking {len(packages)} packages")

    results = Parallel(n_jobs=4)(delayed(check_package)(package) for package in packages)

    for result in results:
        if result[0] == 0:
            found_list.append((result[1], result[2]))
        elif result[0] == 1:
            missing_list.append((result[1], result[2]))
        elif result[0] == 2:
            skip_list.append((result[1], result[2]))
        else:
            print(f"Invalid list id {result[0]}")
            return

    found_list.sort()
    missing_list.sort()
    skip_list.sort()

    with open(f"{device_name}_found.log", "w") as f:
        for item in found_list:
            f.write(f"{item[0]}, {item[1]}\n")

    with open(f"{device_name}_missing.log", "w") as f:
        for item in missing_list:
            f.write(f"{item[0]}, {item[1]}\n")

    with open(f"{device_name}_skipped.log", "w") as f:
        for item in skip_list:
            f.write(f"{item[0]}, {item[1]}\n")

    print("Finished !")


if __name__ == '__main__':
    main()
