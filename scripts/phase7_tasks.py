"""Authored only after 94bc951/freeze.json; never imported by acquisition."""
import phase7_edit as s


tasks=[dict(id='transfer-iterable-options',request=
'''Make slugify honor its iterable options consistently for one-shot inputs. A finite replacements iterable, including replacement pairs that are themselves one-shot iterables, must behave exactly like the equivalent list of two-element tuples in both the initial and final replacement passes, with original rule order preserved. A finite stopwords iterable must behave like the equivalent list for both lowercase=True and lowercase=False, even when the first input word is not a stopword. Consume each one-shot iterable no more than once, do not mutate caller-owned lists, preserve None/empty-option behavior and existing normalization/truncation/CLI behavior. Update relevant docstrings; only production Python files may be edited.''',
public_test='''from slugify import slugify

def test_iterables_in_both_passes_and_membership():
    assert slugify('a b', replacements=iter([('-', '+')])) == 'a+b'
    assert slugify('Keep Drop Tail', stopwords=iter(['Drop']), lowercase=False) == 'Keep-Tail'
''',hidden_test='''import pytest
from slugify import slugify

class SingleUse:
    def __init__(self, values): self.values = values; self.used = False
    def __iter__(self):
        if self.used: raise AssertionError('iterable consumed twice')
        self.used = True
        yield from self.values

def test_private_nested_one_shot_rules():
    rules = SingleUse([SingleUse(('-', '+')), SingleUse(('+', 'x'))])
    assert slugify('a b', replacements=rules) == 'axb'

@pytest.mark.parametrize('lowercase, expected', [(True, 'keep-tail'), (False, 'Keep-Tail')])
def test_private_stopword_consumption(lowercase, expected):
    words = SingleUse(['Drop'])
    assert slugify('Keep Drop Tail Drop', stopwords=words, lowercase=lowercase) == expected

def test_private_rule_order_and_caller_lists():
    rules = [['-', '+'], ['+', 'x']]
    stops = ['Drop']
    assert slugify('Keep Drop Tail', replacements=rules, stopwords=stops, lowercase=False) == 'KeepxTail'
    assert rules == [['-', '+'], ['+', 'x']]
    assert stops == ['Drop']

def test_private_none_empty_and_composed_options():
    assert slugify('À B', replacements=None, stopwords=None) == 'a-b'
    assert slugify('À B', replacements=iter(()), stopwords=iter(())) == 'a-b'
    expected = slugify('À foo B C', stopwords=['foo'], replacements=[('-', '+')], allow_unicode=True, separator=':', max_length=4)
    actual = slugify('À foo B C', stopwords=SingleUse(['foo']), replacements=SingleUse([SingleUse(('-', '+'))]), allow_unicode=True, separator=':', max_length=4)
    assert actual == expected
'''),dict(id='transfer-cli-regex',request=
'''The CLI already accepts --regex-pattern, but slugify_params does not forward it. Make slugify_params include the parsed regex_pattern value unchanged (including None), so main applies the same custom disallowed-character pattern as the library call. Preserve other CLI options, positional/STDIN input, case/Unicode behavior, and the previously accepted iterable-option fix. Update the relevant function documentation. Do not edit tests, dependencies or command-line option names.''',
public_test='''from slugify import slugify
from slugify.__main__ import parse_args, slugify_params

def test_regex_option_is_forwarded():
    pattern = r'[^a-z_]+'
    params = slugify_params(parse_args(['slugify', 'Hello_42', '--regex-pattern', pattern]))
    assert params['regex_pattern'] == pattern
    assert slugify(**params) == 'hello_'
''',hidden_test='''import io
from slugify import slugify
from slugify.__main__ import main, parse_args, slugify_params

def test_private_regex_none_and_existing_options():
    params = slugify_params(parse_args(['slugify', 'Hello World', '--separator', ':', '--max-length', '7']))
    assert 'regex_pattern' in params and params['regex_pattern'] is None
    assert slugify(**params) == 'hello:w'

def test_private_main_custom_pattern(capsys):
    main(['slugify', 'Hello_42', '--regex-pattern', r'[^a-z_]+'])
    assert capsys.readouterr().out == 'hello_\\n'

def test_private_stdin_unicode_case(monkeypatch, capsys):
    monkeypatch.setattr('sys.stdin', io.StringIO('ÉCHO_42!'))
    main(['slugify', '--stdin', '--allow-unicode', '--no-lowercase', '--regex-pattern', r'[^ÉA-Z_0-9]+'])
    assert capsys.readouterr().out == 'ÉCHO_42\\n'

def test_private_regex_with_replacements_and_stopwords(capsys):
    argv = ['slugify', 'Keep_Drop_42', '--regex-pattern', r'[^A-Za-z0-9]+', '--no-lowercase', '--stopwords', 'Drop', '--replacements', '42->Tail', '--separator', ':']
    params = slugify_params(parse_args(argv))
    assert params['regex_pattern'] == r'[^A-Za-z0-9]+'
    main(argv)
    assert capsys.readouterr().out == 'Keep:Tail\\n'
''')]


if __name__=='__main__':
    assert (s.PHASE/'freeze.json').exists()
    assert not (s.PHASE/'transfer-tasks.json').exists()
    s.dump(s.PHASE/'transfer-tasks.json',tasks)
    s.dump(s.PHASE/'task-authorship.json',dict(timestamp=s.old.stamp(),script_sha256=s.sha(__file__),
        freeze_sha256=s.sha(s.PHASE/'freeze.json'),freeze_commit='94bc951',
        source='Investigator-authored after freeze, no upstream issue/reference patch used',new_acquisition_updates=False))
