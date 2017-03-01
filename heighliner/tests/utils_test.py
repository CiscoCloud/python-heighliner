from nose.tools import raises
import heighliner.utils as utils


# META - Config Validation
def test_meta_service_shortcut():
    test_config = {'service': 'foo'}
    config = utils._prepare_manifest(test_config)
    assert 'meta' in config
    assert 'name' in config['meta']
    assert config['meta']['name'] == 'foo'
    assert 'type' in config['meta']
    assert config['meta']['type'] == 'service'


def test_meta_project_shortcut():
    test_config = {'project': 'foo'}
    config = utils._prepare_manifest(test_config)
    assert 'meta' in config
    assert 'name' in config['meta']
    assert config['meta']['name'] == 'foo'
    assert 'type' in config['meta']
    assert config['meta']['type'] == 'project'


def test_meta_project_default():
    test_config = {}
    config = utils._prepare_manifest(test_config)
    assert 'meta' in config
    assert 'type' in config['meta']
    assert config['meta']['type'] == 'project'


def test_meta_version_shortcut():
    test_config = {'version': '0.1.0'}
    config = utils._prepare_manifest(test_config)
    assert 'meta' in config
    assert 'version' in config['meta']
    assert config['meta']['version'] == '0.1.0'


@raises(RuntimeError)
def test_meta_service_project_overlap():
    test_config = {'project': 'foo', 'service': 'bar'}
    utils._prepare_manifest(test_config)
