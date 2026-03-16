from setuptools import find_packages, setup

package_name = "jamshield_recon_x_sim"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (
            f"share/{package_name}/launch",
            ["launch/runtime_probe_colcon.launch.py"],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="jamshield",
    maintainer_email="noreply@jamshield.local",
    description="ROS2 launch packaging for JamShield Recon-X runtime probes.",
    license="Proprietary",
    tests_require=["pytest"],
    entry_points={"console_scripts": []},
)
