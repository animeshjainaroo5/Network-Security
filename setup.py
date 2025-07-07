from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    #returns list of requirements

    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt', 'r') as file:
            lines= file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement in requirement!='-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt not found")

    return requirement_lst

setup(
    name="NetworkSecurity",
    version="v0.1",
    author="Animesh Jain",
    author_email="animeshjain.chd@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements() #to make sure it installs req
)