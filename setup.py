from setuptools import setup

setup(
    name="google_drive_data",
    version="0.1",
    description="Basic file management on Google Drive",
    packages=["google_drive_data"],
    license="MIT",
    author="Frederik Schmidt",
    url="https://github.com/frederik-schmidt/google_drive_data",
    install_requires=["pydrive2"],
    zip_safe=False,
)
