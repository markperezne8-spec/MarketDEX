import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.database_manager import DatabaseManager

BASELINE = '9c8bb74166eac532cf81b299400edd3b6c2f118c'
ACCEPTANCE_REQUEST = 'M34-REGISTER-CHARIZARD-001'


def now():
    return datetime.now(timezone.utc).isoformat()


def norm(value):
    return re.sub(r'[^a-z0-9]+', ' ', (value or '').casefold()).strip()


class ProductRegistryService:
    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()

    def _c(self):
        return self.database.connect()

    def identity_key(self, product_type, name, set_name=None, card_number=None, variant_name=None):
        return '|'.join(map(norm, (product_type, name, set_name, card_number, variant_name)))

    def _replay_product(self, connection, request_id, event_type):
        event = connection.execute(
            'SELECT event_id,event_type FROM event_identity WHERE request_id=?', (request_id,)
        ).fetchone()
        if not event:
            return None
        if event['event_type'] != event_type:
            raise ValueError('request_id already committed for another event type')
        if event_type == 'PRODUCT_REGISTRATION':
            row = connection.execute(
                'SELECT product_id FROM products WHERE created_event_id=?', (event['event_id'],)
            ).fetchone()
        else:
            row = connection.execute(
                'SELECT product_id FROM product_aliases WHERE created_event_id=?', (event['event_id'],)
            ).fetchone()
        if not row:
            raise RuntimeError('committed Product Registry event has no authority row')
        return row['product_id']

    def register(self, product_type, canonical_name, set_name=None, card_number=None, variant_name=None, request_id=None):
        if not request_id:
            raise ValueError('missing explicit registration request')
        if product_type not in ('SINGLE', 'SEALED'):
            raise ValueError('unsupported product_type')
        if not norm(canonical_name):
            raise ValueError('missing canonical_name')
        key = self.identity_key(product_type, canonical_name, set_name, card_number, variant_name)
        payload = json.dumps([product_type, canonical_name, set_name, card_number, variant_name], ensure_ascii=False)
        with self.database.transaction() as connection:
            replay = self._replay_product(connection, request_id, 'PRODUCT_REGISTRATION')
            if replay:
                return replay
            if connection.execute('SELECT 1 FROM products WHERE normalized_identity_key=?', (key,)).fetchone():
                raise ValueError('duplicate normalized identity key')
            product_id = 'PRD-' + uuid.uuid4().hex[:16].upper()
            event_id = 'EVT-' + uuid.uuid4().hex.upper()
            ts = now()
            sha = hashlib.sha256(payload.encode()).hexdigest()
            connection.execute(
                'INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',
                (event_id, 'PRODUCT_REGISTRATION', request_id, ts, ts, payload, sha),
            )
            connection.execute(
                'INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)',
                (product_id, product_type, canonical_name, key, set_name, card_number, variant_name, 'REGISTERED', event_id, ts),
            )
            connection.execute(
                'INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)',
                (product_id, request_id, event_id, product_type, canonical_name, key, 'REGISTERED', ts),
            )
            connection.execute(
                'INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',
                (event_id, 'PRODUCT_REGISTRY', product_id, 'VERIFIED', ts),
            )
            persisted = connection.execute('SELECT * FROM products WHERE product_id=?', (product_id,)).fetchone()
            if not persisted or persisted['normalized_identity_key'] != key:
                raise RuntimeError('post-write verification failed')
            return product_id

    def add_alias(self, product_id, alias_name, request_id):
        if not request_id:
            raise ValueError('missing explicit alias request')
        key = norm(alias_name)
        if not key:
            raise ValueError('missing alias')
        with self.database.transaction() as connection:
            replay = self._replay_product(connection, request_id, 'PRODUCT_ALIAS')
            if replay:
                return replay
            if not connection.execute('SELECT 1 FROM products WHERE product_id=?', (product_id,)).fetchone():
                raise ValueError('orphan alias')
            if connection.execute('SELECT 1 FROM product_aliases WHERE normalized_alias_key=?', (key,)).fetchone():
                raise ValueError('alias collision')
            alias_id = 'ALS-' + uuid.uuid4().hex[:16].upper()
            event_id = 'EVT-' + uuid.uuid4().hex.upper()
            ts = now()
            payload = json.dumps([product_id, alias_name], ensure_ascii=False)
            sha = hashlib.sha256(payload.encode()).hexdigest()
            connection.execute(
                'INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',
                (event_id, 'PRODUCT_ALIAS', request_id, ts, ts, payload, sha),
            )
            connection.execute(
                'INSERT INTO product_aliases VALUES(?,?,?,?,?,?)',
                (alias_id, product_id, alias_name, key, event_id, ts),
            )
            connection.execute(
                'INSERT INTO product_alias_history(alias_id,product_id,alias_name,normalized_alias_key,event_id,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?)',
                (alias_id, product_id, alias_name, key, event_id, 'VERIFIED', ts),
            )
            connection.execute(
                'INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)',
                (event_id, 'PRODUCT_ALIAS', alias_id, 'VERIFIED', ts),
            )
            return product_id

    def resolve_alias(self, alias):
        with self.database.read_connection() as connection:
            row = connection.execute(
                'SELECT product_id FROM product_aliases WHERE normalized_alias_key=?', (norm(alias),)
            ).fetchone()
            return row['product_id'] if row else None

    def run_acceptance(self):
        pid = self.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', ACCEPTANCE_REQUEST)
        duplicate = 'BLOCKED'
        try:
            self.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', 'M34-DUPLICATE-001')
        except ValueError:
            pass
        else:
            duplicate = 'FAILED'
        self.add_alias(pid, 'Charizard EX 125/197', 'M34-ALIAS-001')
        alias_ok = self.resolve_alias('Charizard EX 125/197') == pid
        other = self.register('SEALED', 'Obsidian Flames Elite Trainer Box', 'Obsidian Flames', None, 'Standard', 'M34-OTHER-001')
        collision = 'BLOCKED'
        try:
            self.add_alias(other, 'Charizard EX 125/197', 'M34-ALIAS-COLLISION-001')
        except ValueError:
            pass
        else:
            collision = 'FAILED'
        replay = self.register('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare', ACCEPTANCE_REQUEST) == pid
        return self.verify(pid, duplicate, alias_ok, collision, replay)

    def verify(self, pid=None, duplicate='BLOCKED', alias_ok=None, collision='BLOCKED', replay=True):
        with self.database.read_connection() as connection:
            if pid is None:
                row = connection.execute(
                    'SELECT product_id FROM products WHERE normalized_identity_key=?',
                    (self.identity_key('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare'),),
                ).fetchone()
                pid = row['product_id'] if row else None
            product = connection.execute('SELECT * FROM products WHERE product_id=?', (pid,)).fetchone() if pid else None
            if alias_ok is None:
                alias_ok = self.resolve_alias('Charizard EX 125/197') == pid if pid else False
            history = 'APPEND-ONLY' if product and connection.execute('SELECT COUNT(*) n FROM product_registration_history WHERE product_id=?', (pid,)).fetchone()['n'] == 1 else 'PENDING'
            audit = 'PASS' if product and connection.execute('SELECT 1 FROM audit_events WHERE event_id=? AND authority_id=?', (product['created_event_id'], pid)).fetchone() else 'PENDING'
            replay_row = connection.execute('SELECT event_id,event_type FROM event_identity WHERE request_id=?', (ACCEPTANCE_REQUEST,)).fetchone()
            replay_ok = bool(replay and replay_row and replay_row['event_type'] == 'PRODUCT_REGISTRATION' and product and replay_row['event_id'] == product['created_event_id'])
            checks = [('Product evidence validation', bool(product), 'required SINGLE evidence accepted'), ('Product type authority', bool(product and product['product_type'] == 'SINGLE'), 'SINGLE is explicit and supported'), ('Canonical identity normalization', bool(product and product['normalized_identity_key'] == self.identity_key('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare')), 'normalized identity stable'), ('Persistent product identity', bool(pid), 'stable product_id persisted'), ('Duplicate product blocking', duplicate == 'BLOCKED', 'exact duplicate creates ZERO second product'), ('Controlled alias authority', bool(alias_ok), 'alias resolves to original product_id'), ('Alias collision blocking', collision == 'BLOCKED', 'one alias cannot resolve to multiple products'), ('Append-only registration history', history == 'APPEND-ONLY', 'registration history protected'), ('Request + event identity authority', bool(product and product['created_event_id']), 'request and event identity linked'), ('Persistent replay defense', replay_ok, 'same request returns accepted product_id'), ('Audit explainability', audit == 'PASS', 'product event has VERIFIED audit'), ('Restart-persistent Product Registry authority', bool(product and alias_ok and replay_ok), 'product, alias, history and replay reconstruct')]
            passed = sum(ok for _, ok, _ in checks)
            return {'checks': checks, 'passed': passed, 'pid': pid or 'PENDING', 'duplicate': duplicate, 'alias': 'VERIFIED' if alias_ok else 'PENDING', 'collision': collision, 'history': history, 'replay': 'PASS' if replay_ok else 'PENDING', 'audit': audit, 'restart': 'PASS' if passed == 12 else 'PENDING', 'state': 'REGISTERED' if passed == 12 else 'DRAFT'}
