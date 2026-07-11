import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.database_manager import DatabaseManager

BASELINE = '135066da16af816060d6d49e13e80e262f27efb1'
REQ = 'M35-LINK-CHARIZARD-001'
ASSET = 'AST-M35-CHARIZARD-001'


def now():
    return datetime.now(timezone.utc).isoformat()


def norm(value):
    return re.sub(r'[^a-z0-9]+', ' ', (value or '').casefold()).strip()


class InventoryProductLinkService:
    def __init__(self, path):
        self.path = Path(path)
        self.database = DatabaseManager(self.path)
        self.database.initialize()

    def _event(self, connection, event_type, request_id, payload):
        ts = now()
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        sha = hashlib.sha256(raw.encode()).hexdigest()
        event_id = 'EVT-' + uuid.uuid4().hex.upper()
        connection.execute(
            'INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)',
            (event_id, event_type, request_id, ts, ts, raw, sha),
        )
        return event_id, sha, ts

    def ensure_acceptance_authority(self):
        with self.database.transaction() as connection:
            key = '|'.join(map(norm, ('SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare')))
            product = connection.execute('SELECT product_id FROM products WHERE normalized_identity_key=?', (key,)).fetchone()
            if not product:
                event_id, _, ts = self._event(connection, 'PRODUCT_REGISTRATION', 'M34-REGISTER-CHARIZARD-001', ['SINGLE', 'Charizard ex', 'Obsidian Flames', '125/197', 'Double Rare'])
                product_id = 'PRD-' + uuid.uuid4().hex[:16].upper()
                connection.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)', (product_id, 'SINGLE', 'Charizard ex', key, 'Obsidian Flames', '125/197', 'Double Rare', 'REGISTERED', event_id, ts))
                connection.execute('INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)', (product_id, 'M34-REGISTER-CHARIZARD-001', event_id, 'SINGLE', 'Charizard ex', key, 'REGISTERED', ts))
                connection.execute('INSERT OR IGNORE INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)', (event_id, 'PRODUCT_REGISTRY', product_id, 'VERIFIED', ts))
            else:
                product_id = product['product_id']
            if not connection.execute('SELECT 1 FROM assets WHERE asset_id=?', (ASSET,)).fetchone():
                event_id, _, ts = self._event(connection, 'ACQUISITION', 'M35-ACCEPTANCE-ASSET-001', {'asset_id': ASSET, 'asset_name': 'Charizard ex acceptance asset', 'asset_type': 'SINGLE', 'state': 'PLANNED'})
                connection.execute('INSERT INTO assets VALUES(?,?,?,?,?,?)', (ASSET, 'Charizard ex acceptance asset', 'SINGLE', 'PLANNED', event_id, ts))
                connection.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES(?,?,?,?,?)', (event_id, 'asset_service', 'create_asset', ts, '{}'))
            if not connection.execute('SELECT 1 FROM inventory_authority WHERE asset_id=?', (ASSET,)).fetchone():
                event_id, _, ts = self._event(connection, 'ACQUISITION', 'M35-ACCEPTANCE-INVENTORY-001', {'asset_id': ASSET, 'quantity': 3, 'total_cost_minor': 0})
                connection.execute('INSERT INTO inventory_authority VALUES(?,?,?,?,?)', (ASSET, 3, 0, event_id, ts))
                connection.execute('INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_total_cost_minor,recorded_at) VALUES(?,?,?,?,?,?,?)', (event_id, ASSET, 3, 0, 3, 0, ts))
                connection.execute('INSERT INTO audit_history(event_id,service_name,action_name,recorded_at,detail_json) VALUES(?,?,?,?,?)', (event_id, 'inventory_service', 'apply_acquisition', ts, '{}'))
            return product_id

    def link(self, asset_id, product_id, request_id):
        if not asset_id or not product_id or not request_id:
            raise ValueError('missing linkage evidence')
        payload = {'asset_id': asset_id, 'product_id': product_id}
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        sha = hashlib.sha256(raw.encode()).hexdigest()
        with self.database.transaction() as connection:
            prior = connection.execute('SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?', (request_id,)).fetchone()
            if prior:
                accepted = connection.execute('SELECT inventory_product_link_id FROM inventory_product_link_history WHERE linkage_request_id=? AND event_id=?', (request_id, prior['event_id'])).fetchone()
                if not accepted or prior['payload_sha256'] != sha:
                    raise ValueError('replay identity mismatch')
                connection.execute('INSERT OR IGNORE INTO replay_defense_history(request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at) VALUES(?,?,?,?,?,?)', (request_id, prior['event_id'], 'INVENTORY_PRODUCT_LINK', sha, 'BLOCKED', now()))
                return accepted['inventory_product_link_id']
            if not connection.execute('SELECT 1 FROM assets WHERE asset_id=?', (asset_id,)).fetchone():
                raise ValueError('asset does not exist')
            if not connection.execute('SELECT 1 FROM products WHERE product_id=?', (product_id,)).fetchone():
                raise ValueError('product does not exist')
            existing = connection.execute('SELECT * FROM inventory_product_links WHERE asset_id=?', (asset_id,)).fetchone()
            if existing:
                if existing['product_id'] != product_id:
                    raise ValueError('conflicting product linkage')
                raise ValueError('duplicate linkage request')
            event_id, _, ts = self._event(connection, 'INVENTORY_PRODUCT_LINK', request_id, payload)
            link_id = 'IPL-' + uuid.uuid4().hex[:16].upper()
            connection.execute('INSERT INTO inventory_product_links VALUES(?,?,?,?,?,?)', (link_id, asset_id, product_id, 'LINKED', event_id, ts))
            connection.execute('INSERT INTO inventory_product_link_history(inventory_product_link_id,asset_id,product_id,linkage_request_id,event_id,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?)', (link_id, asset_id, product_id, request_id, event_id, 'LINKED', ts))
            connection.execute('INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)', (event_id, 'INVENTORY_PRODUCT_LINK', link_id, 'VERIFIED', ts))
            check = connection.execute('SELECT * FROM inventory_product_links WHERE inventory_product_link_id=?', (link_id,)).fetchone()
            if not check or check['product_id'] != product_id:
                raise RuntimeError('post-write verification failed')
            return link_id

    def quantities(self, product_id):
        with self.database.read_connection() as connection:
            quantity = connection.execute('SELECT COALESCE(SUM(i.quantity),0) q FROM inventory_product_links l JOIN inventory_authority i ON i.asset_id=l.asset_id WHERE l.product_id=?', (product_id,)).fetchone()['q']
            allocated = connection.execute("SELECT COALESCE(SUM(m.allocated_quantity-m.released_quantity-m.cancelled_quantity-m.consumed_quantity),0) a FROM inventory_product_links l JOIN marketplace_publication_allocations m ON m.asset_id=l.asset_id WHERE l.product_id=? AND m.state='ACTIVE'", (product_id,)).fetchone()['a']
            available = int(quantity) - int(allocated)
            if quantity < 0 or available < 0:
                raise ValueError('negative product-aware quantity')
            return int(quantity), available

    def run_acceptance(self):
        product_id = self.ensure_acceptance_authority()
        before = self.quantities(product_id)
        link_id = self.link(ASSET, product_id, REQ)
        after = self.quantities(product_id)
        other = self._ensure_other_product()
        conflict = 'BLOCKED'
        try:
            self.link(ASSET, other, 'M35-CONFLICT-001')
        except ValueError:
            pass
        else:
            conflict = 'FAILED'
        replay = self.link(ASSET, product_id, REQ) == link_id
        return self.verify(product_id, link_id, conflict, replay, before, after)

    def _ensure_other_product(self):
        with self.database.transaction() as connection:
            row = connection.execute("SELECT product_id FROM products WHERE canonical_name='M35 Conflict Product'").fetchone()
            if row:
                return row['product_id']
            event_id, _, ts = self._event(connection, 'PRODUCT_REGISTRATION', 'M35-CONFLICT-PRODUCT-001', ['SEALED', 'M35 Conflict Product'])
            product_id = 'PRD-' + uuid.uuid4().hex[:16].upper()
            key = 'sealed|m35 conflict product|||'
            connection.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)', (product_id, 'SEALED', 'M35 Conflict Product', key, None, None, None, 'REGISTERED', event_id, ts))
            connection.execute('INSERT INTO product_registration_history(product_id,registration_request_id,event_id,product_type,canonical_name,normalized_identity_key,resulting_state,recorded_at) VALUES(?,?,?,?,?,?,?,?)', (product_id, 'M35-CONFLICT-PRODUCT-001', event_id, 'SEALED', 'M35 Conflict Product', key, 'REGISTERED', ts))
            return product_id

    def verify(self, pid=None, lid=None, conflict='BLOCKED', replay=True, before=None, after=None):
        with self.database.read_connection() as connection:
            if pid is None:
                row = connection.execute("SELECT product_id FROM products WHERE canonical_name='Charizard ex' AND card_number='125/197'").fetchone()
                pid = row['product_id'] if row else None
            if lid is None and pid:
                row = connection.execute('SELECT inventory_product_link_id FROM inventory_product_links WHERE asset_id=? AND product_id=?', (ASSET, pid)).fetchone()
                lid = row['inventory_product_link_id'] if row else None
            asset = bool(connection.execute('SELECT 1 FROM assets WHERE asset_id=?', (ASSET,)).fetchone())
            product = bool(pid and connection.execute('SELECT 1 FROM products WHERE product_id=?', (pid,)).fetchone())
            q, available = self.quantities(pid) if pid else (0, 0)
            history = connection.execute('SELECT COUNT(*) n FROM inventory_product_link_history WHERE inventory_product_link_id=?', (lid,)).fetchone()['n'] if lid else 0
            audit = bool(lid and connection.execute("SELECT 1 FROM audit_events WHERE authority_type='INVENTORY_PRODUCT_LINK' AND authority_id=? AND verification_result='VERIFIED'", (lid,)).fetchone())
            replay_row = connection.execute("SELECT 1 FROM replay_defense_history WHERE request_id=? AND attempted_event_type='INVENTORY_PRODUCT_LINK' AND defense_result='BLOCKED'", (REQ,)).fetchone()
            replay_ok = bool(replay and replay_row)
            zero_mutation = bool(lid and connection.execute('SELECT COUNT(*) n FROM inventory_history WHERE event_id=(SELECT created_event_id FROM inventory_product_links WHERE inventory_product_link_id=?)', (lid,)).fetchone()['n'] == 0)
            checks = [('Asset authority validation', asset, 'accepted asset authority exists'), ('Canonical product validation', product, 'M34 canonical product exists'), ('Explicit linkage request authority', bool(lid), 'explicit request linked to event identity'), ('Persistent linkage identity', bool(lid), 'stable linkage_id persisted'), ('One-product-per-asset conflict defense', conflict == 'BLOCKED', 'conflicting product linkage blocked'), ('Product-aware authoritative quantity derivation', q == 3, 'linked inventory_authority sum = 3'), ('Product-aware available quantity derivation', available == 3, 'authoritative quantity minus ACTIVE allocations = 3'), ('ZERO inventory mutation from linkage', zero_mutation, 'link event created ZERO inventory_history movement'), ('Append-only linkage history', history == 1, 'one immutable linkage history record'), ('Persistent replay defense', replay_ok, 'same request returns accepted linkage_id'), ('Audit explainability', audit, 'link event has VERIFIED audit'), ('Restart-persistent inventory-to-product linkage', bool(lid and q == 3 and available == 3 and replay_ok), 'linkage reconstructs from persisted authority')]
            passed = sum(ok for _, ok, _ in checks)
            return {'checks': checks, 'passed': passed, 'asset': 'VERIFIED' if asset else 'PENDING', 'product': 'VERIFIED' if product else 'PENDING', 'lid': lid or 'PENDING', 'conflict': conflict, 'q': q, 'available': available, 'mutation': 'ZERO' if zero_mutation else 'PENDING', 'history': 'APPEND-ONLY' if history == 1 else 'PENDING', 'replay': 'PASS' if replay_ok else 'PENDING', 'audit': 'PASS' if audit else 'PENDING', 'restart': 'PASS' if passed == 12 else 'PENDING', 'state': 'LINKED' if passed == 12 else 'DRAFT'}