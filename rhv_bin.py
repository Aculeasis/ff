# Docs https://docs.github.com/en/rest/reference/repos#releases

import urllib.request
import urllib.error
import json
import sys
import operator

ENDPOINT = 'https://api.github.com/repos/Aculeasis/rhvoice-wrapper-bin/releases'
OSES = {
    ['ubuntu-20.04', 'ubuntu', 'linux']: 'linux',
    ['windows-2019', 'windows', 'win']: 'win'
}

ARCH = {
    ['x32', 'x86', '32', '86', 'i686']: {
        'win': '32',
        'linux': '_i686'
    },
    ['x64', 'x86_64', '64', 'amd64']: {
        'win': '_amd64',
        'linux': '_x86_64'
    },
    ['aarch64', 'arm64', 'arm64v8']: {
        'linux': '_aarch64'
    },
    ['armv7l', 'armv7', 'arm32', 'arm32v7']: {
        'linux': '_armv7l'
    },
}


def get_release_dict():
    response = urllib.request.urlopen(
        urllib.request.Request(url=ENDPOINT, headers={'Accept': 'application/vnd.github.v3+json'})
    )
    if response.getcode() != 200:
        raise RuntimeError('Request code error: {}'.format(response.getcode()))
    return json.loads(response.read().decode('utf-8'))


def prepare_release():
    result = dict()
    for release in get_release_dict():
        tag_name = release.get('tag_name')
        if tag_name:
            result[tag_name] = [x.get('browser_download_url', '') for x in release.get('assets', [])]
    return sorted(result.items(), key=operator.itemgetter(0), reverse=True)


def make_tail(os: str, arch: str):
    os = (os or 'ubuntu-20.04').lower()
    arch = (arch or 'x64').lower()
    for k, v in OSES.values():
        if os in k:
            os = v
            break
    else:
        raise RuntimeError('Wrong OS: {}'.format(os))
    for k, v in ARCH.values():
        if arch in k:
            arch = v[os]
            break
    else:
        raise RuntimeError('Wrong arch: {}'.format(arch))
    return '-py3-none-{os}{arch}.whl'.format(os=os, arch=arch)


def get_url():
    arch = sys.argv[2] if len(sys.argv) >= 3 else ''
    os = sys.argv[1] if len(sys.argv) >= 2 else ''
    tail = make_tail(os, arch)
    for _, targets in prepare_release():
        for target in targets:
            if target.endswith(tail):
                return target


if __name__ == '__main__':
    print(get_url())
