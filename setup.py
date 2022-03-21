from setuptools import setup

setup(
    name="google_drive_data_transfer",
    version="0.2",
    description="Basic file management on Google Drive",
    packages=["google_drive_data_transfer"],
    license="MIT",
    author="Frederik Schmidt",
    url="https://github.com/frederik-schmidt/google_drive_data_transfer",
    install_requires=["pydrive2"],
    zip_safe=False,
)
