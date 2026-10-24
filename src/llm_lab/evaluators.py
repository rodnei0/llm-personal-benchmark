"""Avaliadores objetivos e encaminhamento explícito à revisão humana."""
import math

SUPPORTED = {'numeric_json_v1', 'boolean_json_v1', 'human_rubric_v1'}


def evaluate_case(response, expected, evaluator):
    from .core import evaluate, strict_json
    if evaluator == 'log_exact_v1':
        return evaluate(response, expected)
    if evaluator == 'human_rubric_v1':
        return {'passed': None, 'status': 'pending_human_review', 'checks': {},
                'error': None, 'rubric': expected,
                'note': 'Nenhuma nota automática; revisar resposta original conforme rubrica'}
    try:
        value = strict_json(response)
    except (ValueError, TypeError) as exc:
        return {'passed': False, 'checks': {'valid_json': False}, 'error': str(exc)}
    fields = {'answer'} | ({'unit'} if 'unit' in expected else set())
    schema = type(value) is dict and set(value) == fields
    if evaluator == 'numeric_json_v1':
        schema = schema and type(value['answer']) in (int, float)
        if schema:
            try:
                schema = math.isfinite(value['answer'])
            except OverflowError:
                schema = False
        correct = bool(schema and abs(value['answer'] - expected['answer']) <= expected.get('absolute_tolerance', 0))
    elif evaluator == 'boolean_json_v1':
        schema = schema and type(value['answer']) is bool
        correct = bool(schema and value['answer'] is expected['answer'])
    else:
        raise ValueError('Avaliador desconhecido')
    checks = {'valid_json': True, 'schema': bool(schema), 'answer_correct': correct}
    if 'unit' in expected:
        checks['unit_correct'] = bool(schema and value['unit'] == expected['unit'])
    return {'passed': all(checks.values()), 'checks': checks, 'error': None}
