import argparse
import asyncio
import logging

from viam.rpc.server import Server
from oak_camera import OakCamera


def parse_args():
    """
    simple argument parser
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        '-n',
        dest='host',
        help='hostname/ip rpc server will bind to',
        required=False,
        type=str,
        action='store',
        default='localhost'
    )
    parser.add_argument(
        '--port',
        '-p',
        dest='port',
        help='port number to store',
        required=False,
        type=int,
        action='store',
        default=9090
    )
    parser.add_argument(
        '--log',
        '-l',
        dest='log',
        help='log level to use',
        required=False,
        type=str,
        action='store',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL'],
        default='WARNING'
    )
    return parser.parse_args()


async def main(host, port, log_level):
    """
    start an RPC server to host custom remote components
    :param host:
    :param port:
    :param log_level:
    :return:
    """
    srv = Server([OakCamera('oak-1')])
    await srv.serve(host=host, port=port, log_level=log_level)


if __name__ == '__main__':
    try:
        args = parse_args()
        asyncio.run(main(args.host, args.port, args.log))
    except Exception as e:
        logging.error(f'failed to start server: {e}')
