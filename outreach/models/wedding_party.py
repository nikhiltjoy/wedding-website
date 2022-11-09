from collections import defaultdict, OrderedDict
from pathlib import Path
from typing import Mapping, List

from outreach.data.repository.google_sheets import GSheetClient
from outreach.message.EmailMessageClient import check_if_valid_email
from outreach.models.party import Party, Guest
import pandas as pd
import numpy as np


class WeddingParty:
    def __init__(self, gc_client: GSheetClient, sheet_id: str):
        self.gc_client = gc_client
        self.sheet_id = sheet_id
        guest_df = self.gc_client.get_dataframe_from_sheet(self.sheet_id)
        self.all_parties: Mapping[int, Party] = OrderedDict()
        self.all_guests: Mapping[int, Guest] = OrderedDict()
        guest_df = guest_df.replace([np.nan], [None])
        _tmp_parties: Mapping[int, List[Guest]] = defaultdict(list)
        for i, row in guest_df.iterrows():
            guest = Guest(row.to_dict())
            self.all_guests[guest.user_id] = guest
            _tmp_parties[guest.party_id].append(guest)
        for p in _tmp_parties:
            self.all_parties[p] = Party(_tmp_parties[p])

    def get_guest(self, user_id: int):
        return self.all_guests.get(user_id)

    def get_party(self, party_id: int):
        return self.all_parties.get(party_id)

    def get_all_party_ids(self) -> List[int]:
        return list(self.all_parties.keys())

    def get_parties_with_emails(self) -> List[int]:
        valid_parties = []
        for p in self.get_all_party_ids():
            for g in self.all_parties[p].get_guests():
                if check_if_valid_email(g.email):
                    valid_parties.append(p)
                    break
        return valid_parties

    def _get_guest_df(self):
        records = [g.get_guest_as_dict() for g in self.all_guests.values()]
        return pd.DataFrame.from_records(data=records)

    def persist_local(self, local_pq_path: Path):
        self._get_guest_df().to_parquet(local_pq_path)

    def persist(self, local_pq_path: Path = None):
        if local_pq_path:
            self.persist_local(local_pq_path)
        self.gc_client.set_sheet_from_dataframe(self._get_guest_df(), self.sheet_id)
