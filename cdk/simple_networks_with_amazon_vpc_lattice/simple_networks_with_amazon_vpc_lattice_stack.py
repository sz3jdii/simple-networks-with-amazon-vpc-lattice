import os
from pathlib import Path
from typing import Final

from aws_cdk import Stack
from constructs import Construct, DependencyGroup
from git import Repo

from cdk.simple_networks_with_amazon_vpc_lattice.constants import SERVICE_NAME
from cdk.simple_networks_with_amazon_vpc_lattice.ec2.ec2_construct import EC2Construct
from cdk.simple_networks_with_amazon_vpc_lattice.ecs.ecs_construct import EcsConstruct
from cdk.simple_networks_with_amazon_vpc_lattice.lambda_function.lambda_construct import LambdaConstruct
from cdk.simple_networks_with_amazon_vpc_lattice.lattice.lattice_construct import LatticeConstruct


def get_username() -> str:
    DEFAULT_USERNAME: Final[str] = 'github'
    try:
        login = os.getlogin().replace('.', '')
        if login == 'root':
            login = os.getenv("USER")
        if login is None:
            return DEFAULT_USERNAME
        return login
    except Exception:
        return DEFAULT_USERNAME


def get_stack_name() -> str:
    repo = Repo(Path.cwd())
    username = get_username()
    try:
        return f'{username}{repo.active_branch}{SERVICE_NAME}'
    except TypeError:
        return f'{username}{SERVICE_NAME}'


class SimpleNetworksWithAmazonVpcLatticeStack(Stack):

    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)
        self.ecs_cluster = EcsConstruct(self, f'{SERVICE_NAME}ECSCluster')
        self.ec2_instance = EC2Construct(self, f'{SERVICE_NAME}EC2Instance')
        self.lambda_function = LambdaConstruct(self, f'{SERVICE_NAME}Lambda')
        self.service = DependencyGroup()
        self.service.add(self.ecs_cluster)
        self.service.add(self.ec2_instance)
        self.service.add(self.lambda_function)
        LatticeConstruct(self, f'{SERVICE_NAME}Lattice').node.add_dependency(self.service)
