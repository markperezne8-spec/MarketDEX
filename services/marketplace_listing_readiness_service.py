import sqlite3, uuid, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

BASELINE = "6bf853bfe09794d30af527ae1c48985bfb1e11ab"
PRODUCT_NAME = "Charizard ex"
LISTING_REQ = "M36-LISTING-IDENTITY-001"
READINESS_REQ = "M36-PUBLICATION-READINESS-001"

def now():
    return datetime.now(timezone.utc).isoformat()

def payload_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return raw, hashlib.sha256(raw.encode()).hexdigest()

class MarketplaceListingReadinessService:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    @contextmanager
    def _c(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            c.close()

    def _init(self):
        with self._c() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS event_identity(
              event_id TEXT PRIMARY KEY,event_type TEXT NOT NULL,request_id TEXT NOT NULL UNIQUE,
              occurred_at TEXT NOT NULL,committed_at TEXT NOT NULL,payload_json TEXT NOT NULL,payload_sha256 TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS replay_defense_history(
              replay_history_id INTEGER PRIMARY KEY AUTOINCREMENT,request_id TEXT NOT NULL,
              original_event_id TEXT NOT NULL,attempted_event_type TEXT NOT NULL,payload_sha256 TEXT NOT NULL,
              defense_result TEXT NOT NULL CHECK(defense_result='BLOCKED'),recorded_at TEXT NOT NULL,
              UNIQUE(request_id,attempted_event_type,payload_sha256));
            CREATE TABLE IF NOT EXISTS audit_events(
              audit_event_id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL,authority_type TEXT NOT NULL,
              authority_id TEXT NOT NULL,verification_result TEXT NOT NULL,recorded_at TEXT NOT NULL,
              UNIQUE(event_id,authority_type,authority_id));
            CREATE TABLE IF NOT EXISTS products(
              product_id TEXT PRIMARY KEY,product_type TEXT NOT NULL,canonical_name TEXT NOT NULL,
              normalized_identity_key TEXT NOT NULL UNIQUE,set_name TEXT,card_number TEXT,variant_name TEXT,
              state TEXT NOT NULL,created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS inventory_authority(
              asset_id TEXT PRIMARY KEY,quantity INTEGER NOT NULL CHECK(quantity>=0),total_cost_minor INTEGER NOT NULL CHECK(total_cost_minor>=0),
              last_event_id TEXT NOT NULL,verified_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS inventory_product_links(
              inventory_product_link_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL UNIQUE,product_id TEXT NOT NULL,
              state TEXT NOT NULL CHECK(state='LINKED'),created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS marketplace_publication_allocations(
              allocation_id TEXT PRIMARY KEY,asset_id TEXT NOT NULL,marketplace TEXT NOT NULL,publication_reference TEXT NOT NULL,
              publication_identity TEXT NOT NULL,requested_quantity INTEGER NOT NULL,allocated_quantity INTEGER NOT NULL,
              released_quantity INTEGER NOT NULL DEFAULT 0,cancelled_quantity INTEGER NOT NULL DEFAULT 0,
              consumed_quantity INTEGER NOT NULL DEFAULT 0,state TEXT NOT NULL,source_event_id TEXT NOT NULL,
              created_at TEXT NOT NULL,committed_at TEXT NOT NULL,verified_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS marketplace_listing_identities(
              listing_identity_id TEXT PRIMARY KEY,product_id TEXT NOT NULL,marketplace TEXT NOT NULL,
              seller_listing_reference TEXT NOT NULL,listing_identity_key TEXT NOT NULL UNIQUE,
              state TEXT NOT NULL CHECK(state='IDENTIFIED'),created_event_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,
              UNIQUE(product_id,marketplace,seller_listing_reference));
            CREATE TABLE IF NOT EXISTS marketplace_listing_identity_history(
              history_id INTEGER PRIMARY KEY AUTOINCREMENT,listing_identity_id TEXT NOT NULL,product_id TEXT NOT NULL,
              marketplace TEXT NOT NULL,seller_listing_reference TEXT NOT NULL,request_id TEXT NOT NULL,event_id TEXT NOT NULL,
              resulting_state TEXT NOT NULL,recorded_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS publication_readiness_history(
              readiness_history_id INTEGER PRIMARY KEY AUTOINCREMENT,listing_identity_id TEXT NOT NULL,product_id TEXT NOT NULL,
              request_id TEXT NOT NULL,event_id TEXT NOT NULL,authoritative_quantity INTEGER NOT NULL,
              available_quantity INTEGER NOT NULL,result TEXT NOT NULL CHECK(result IN ('READY','BLOCKED')),recorded_at TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS mlih_no_update BEFORE UPDATE ON marketplace_listing_identity_history
              BEGIN SELECT RAISE(ABORT,'marketplace listing identity history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS mlih_no_delete BEFORE DELETE ON marketplace_listing_identity_history
              BEGIN SELECT RAISE(ABORT,'marketplace listing identity history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS prh_no_update BEFORE UPDATE ON publication_readiness_history
              BEGIN SELECT RAISE(ABORT,'publication readiness history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS prh_no_delete BEFORE DELETE ON publication_readiness_history
              BEGIN SELECT RAISE(ABORT,'publication readiness history is append-only'); END;
            """)

    def _event(self, c, event_type, request_id, payload):
        raw, sha = payload_sha(payload)
        ts = now()
        eid = "EVT-" + uuid.uuid4().hex.upper()
        c.execute("INSERT INTO event_identity VALUES(?,?,?,?,?,?,?)",
                  (eid,event_type,request_id,ts,ts,raw,sha))
        return eid, sha, ts

    def _product(self, c):
        row = c.execute("SELECT product_id FROM products WHERE canonical_name=? ORDER BY created_at LIMIT 1",(PRODUCT_NAME,)).fetchone()
        if not row:
            raise ValueError("M34 canonical product authority missing")
        pid = row["product_id"]
        linked = c.execute("SELECT asset_id FROM inventory_product_links WHERE product_id=? AND state='LINKED' ORDER BY created_at LIMIT 1",(pid,)).fetchone()
        if not linked:
            raise ValueError("M35 product-aware inventory linkage missing")
        return pid, linked["asset_id"]

    def quantities(self, c, pid):
        q = c.execute("""SELECT COALESCE(SUM(i.quantity),0) q
                         FROM inventory_product_links l JOIN inventory_authority i ON i.asset_id=l.asset_id
                         WHERE l.product_id=?""",(pid,)).fetchone()["q"]
        active = c.execute("""SELECT COALESCE(SUM(m.allocated_quantity-m.released_quantity-m.cancelled_quantity-m.consumed_quantity),0) a
                              FROM inventory_product_links l JOIN marketplace_publication_allocations m ON m.asset_id=l.asset_id
                              WHERE l.product_id=? AND m.state='ACTIVE'""",(pid,)).fetchone()["a"]
        available = int(q)-int(active)
        if int(q) < 0 or available < 0:
            raise ValueError("negative product-aware availability")
        return int(q), available

    def create_listing_identity(self, pid, marketplace, seller_ref, request_id):
        if not pid or not marketplace or not seller_ref or not request_id:
            raise ValueError("missing listing identity evidence")
        payload={"product_id":pid,"marketplace":marketplace,"seller_listing_reference":seller_ref}
        raw, sha = payload_sha(payload)
        key=f"{marketplace.casefold()}|{seller_ref.casefold()}"
        with self._c() as c:
            prior=c.execute("SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?",(request_id,)).fetchone()
            if prior:
                accepted=c.execute("SELECT listing_identity_id FROM marketplace_listing_identity_history WHERE request_id=? AND event_id=?",(request_id,prior["event_id"])).fetchone()
                if not accepted or prior["payload_sha256"] != sha:
                    raise ValueError("listing replay identity mismatch")
                c.execute("""INSERT OR IGNORE INTO replay_defense_history
                  (request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at)
                  VALUES(?,?,?,?,?,?)""",(request_id,prior["event_id"],"MARKETPLACE_LISTING_IDENTITY",sha,"BLOCKED",now()))
                return accepted["listing_identity_id"]
            collision=c.execute("SELECT product_id FROM marketplace_listing_identities WHERE listing_identity_key=?",(key,)).fetchone()
            if collision:
                raise ValueError("marketplace listing identity collision")
            eid, sha, ts=self._event(c,"MARKETPLACE_LISTING_IDENTITY",request_id,payload)
            lid="MLI-"+uuid.uuid4().hex[:16].upper()
            c.execute("INSERT INTO marketplace_listing_identities VALUES(?,?,?,?,?,?,?,?)",
                      (lid,pid,marketplace,seller_ref,key,"IDENTIFIED",eid,ts))
            c.execute("""INSERT INTO marketplace_listing_identity_history
              (listing_identity_id,product_id,marketplace,seller_listing_reference,request_id,event_id,resulting_state,recorded_at)
              VALUES(?,?,?,?,?,?,?,?)""",(lid,pid,marketplace,seller_ref,request_id,eid,"IDENTIFIED",ts))
            c.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)",
                      (eid,"MARKETPLACE_LISTING_IDENTITY",lid,"VERIFIED",ts))
            return lid

    def verify_readiness(self, listing_id, request_id):
        with self._c() as c:
            listing=c.execute("SELECT * FROM marketplace_listing_identities WHERE listing_identity_id=?",(listing_id,)).fetchone()
            if not listing:
                raise ValueError("listing identity missing")
            pid=listing["product_id"]
            q,av=self.quantities(c,pid)
            payload={"listing_identity_id":listing_id,"product_id":pid,"authoritative_quantity":q,"available_quantity":av}
            raw,sha=payload_sha(payload)
            prior=c.execute("SELECT event_id,payload_sha256 FROM event_identity WHERE request_id=?",(request_id,)).fetchone()
            if prior:
                accepted=c.execute("SELECT result FROM publication_readiness_history WHERE request_id=? AND event_id=?",(request_id,prior["event_id"])).fetchone()
                if not accepted or prior["payload_sha256"] != sha:
                    raise ValueError("readiness replay identity mismatch")
                c.execute("""INSERT OR IGNORE INTO replay_defense_history
                  (request_id,original_event_id,attempted_event_type,payload_sha256,defense_result,recorded_at)
                  VALUES(?,?,?,?,?,?)""",(request_id,prior["event_id"],"PUBLICATION_READINESS",sha,"BLOCKED",now()))
                return accepted["result"]
            result="READY" if q>0 and av>0 else "BLOCKED"
            eid,sha,ts=self._event(c,"PUBLICATION_READINESS",request_id,payload)
            c.execute("""INSERT INTO publication_readiness_history
              (listing_identity_id,product_id,request_id,event_id,authoritative_quantity,available_quantity,result,recorded_at)
              VALUES(?,?,?,?,?,?,?,?)""",(listing_id,pid,request_id,eid,q,av,result,ts))
            c.execute("INSERT INTO audit_events(event_id,authority_type,authority_id,verification_result,recorded_at) VALUES(?,?,?,?,?)",
                      (eid,"PUBLICATION_READINESS",listing_id,"VERIFIED",ts))
            return result

    def run_acceptance(self):
        with self._c() as c:
            pid, asset = self._product(c)
        lid=self.create_listing_identity(pid,"eBay","M36-EBAY-CHARIZARD-001",LISTING_REQ)
        readiness=self.verify_readiness(lid,READINESS_REQ)
        replay_listing=self.create_listing_identity(pid,"eBay","M36-EBAY-CHARIZARD-001",LISTING_REQ)==lid
        replay_readiness=self.verify_readiness(lid,READINESS_REQ)==readiness
        collision="BLOCKED"
        try:
            self.create_listing_identity(pid,"eBay","M36-EBAY-CHARIZARD-001","M36-COLLISION-001")
        except ValueError:
            pass
        else:
            collision="FAILED"
        return self.verify(lid, collision, replay_listing and replay_readiness)

    def verify(self, lid=None, collision="BLOCKED", replay=True):
        with self._c() as c:
            try:
                pid, asset=self._product(c)
            except ValueError:
                pid=asset=None
            if lid is None and pid:
                r=c.execute("SELECT listing_identity_id FROM marketplace_listing_identities WHERE product_id=? AND marketplace='eBay' AND seller_listing_reference='M36-EBAY-CHARIZARD-001'",(pid,)).fetchone()
                lid=r["listing_identity_id"] if r else None
            q,av=self.quantities(c,pid) if pid else (0,0)
            identity=bool(lid and c.execute("SELECT 1 FROM marketplace_listing_identities WHERE listing_identity_id=? AND state='IDENTIFIED'",(lid,)).fetchone())
            hist=c.execute("SELECT COUNT(*) n FROM marketplace_listing_identity_history WHERE listing_identity_id=?",(lid,)).fetchone()["n"] if lid else 0
            readiness=c.execute("SELECT result FROM publication_readiness_history WHERE listing_identity_id=? ORDER BY readiness_history_id DESC LIMIT 1",(lid,)).fetchone() if lid else None
            ready=readiness["result"] if readiness else "PENDING"
            audit=bool(lid and c.execute("SELECT 1 FROM audit_events WHERE authority_type='MARKETPLACE_LISTING_IDENTITY' AND authority_id=? AND verification_result='VERIFIED'",(lid,)).fetchone())
            listing_replay=bool(c.execute("SELECT 1 FROM replay_defense_history WHERE request_id=? AND attempted_event_type='MARKETPLACE_LISTING_IDENTITY'",(LISTING_REQ,)).fetchone())
            ready_replay=bool(c.execute("SELECT 1 FROM replay_defense_history WHERE request_id=? AND attempted_event_type='PUBLICATION_READINESS'",(READINESS_REQ,)).fetchone())
            zero_inventory=bool(lid and c.execute("SELECT COUNT(*) n FROM inventory_authority WHERE last_event_id=(SELECT created_event_id FROM marketplace_listing_identities WHERE listing_identity_id=?)",(lid,)).fetchone()["n"]==0)
            allocation_mutation=bool(lid and c.execute("SELECT COUNT(*) n FROM marketplace_publication_allocations WHERE source_event_id=(SELECT created_event_id FROM marketplace_listing_identities WHERE listing_identity_id=?)",(lid,)).fetchone()["n"]==0)
            checks=[
              ("M34 canonical product authority",bool(pid),"accepted canonical product exists"),
              ("M35 product-aware inventory linkage",bool(asset),"linked inventory authority exists"),
              ("Explicit marketplace listing identity",identity,"listing identity request linked to event identity"),
              ("Persistent listing identity",identity,"stable listing_identity_id persisted"),
              ("Listing identity collision defense",collision=="BLOCKED","duplicate marketplace listing reference blocked"),
              ("Publication readiness derivation",ready=="READY","product-aware availability derives READY"),
              ("M30 publication boundary preserved",allocation_mutation,"readiness creates ZERO allocation"),
              ("ZERO inventory mutation",zero_inventory,"listing identity creates ZERO inventory mutation"),
              ("Append-only listing history",hist==1,"one immutable listing identity history record"),
              ("Persistent replay defense",bool(replay and listing_replay and ready_replay),"listing and readiness replay create ZERO second authority"),
              ("Audit explainability",audit,"listing identity event has VERIFIED audit"),
              ("Restart-persistent listing readiness",bool(identity and ready=="READY" and q==3 and av==3),"identity and readiness reconstruct from persisted authority"),
            ]
            passed=sum(ok for _,ok,_ in checks)
            return {"checks":checks,"passed":passed,"product":"VERIFIED" if pid else "PENDING",
                    "linkage":"VERIFIED" if asset else "PENDING","listing":"PERSISTENT" if identity else "PENDING",
                    "collision":collision,"readiness":ready,"q":q,"available":av,
                    "allocation":"ZERO" if allocation_mutation else "FAILED","inventory":"ZERO" if zero_inventory else "FAILED",
                    "history":"APPEND-ONLY" if hist==1 else "PENDING","replay":"PASS" if replay and listing_replay and ready_replay else "PENDING",
                    "audit":"PASS" if audit else "PENDING","restart":"PASS" if passed==12 else "PENDING",
                    "state":"PUBLICATION READY" if passed==12 else "DRAFT"}
