# Copyright 2022 eprbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from dali.abstract_transaction import AbstractTransaction
from dali.dali_configuration import Keyword, is_fiat
from dali.in_transaction import InTransaction
from dali.intra_transaction import IntraTransaction
from dali.out_transaction import OutTransaction

_ASSETS: str = "assets"
_EXCHANGES: str = "exchanges"
_HOLDERS: str = "holders"


def generate_config_file(
    output_dir_path: str,
    output_file_prefix: str,
    output_file_name: str,
    transactions: List[AbstractTransaction],
    global_configuration: Dict[str, Any],
) -> Any:

    if not isinstance(output_dir_path, str):
        raise Exception(f"Internal error: parameter output_dir_path is not of type string: {repr(output_dir_path)}")
    if not isinstance(output_file_prefix, str):
        raise Exception(f"Internal error: parameter output_file_prefix is not of type string: {repr(output_file_prefix)}")
    if not isinstance(output_file_name, str):
        raise Exception(f"Internal error: parameter output_file_name is not of type string: {repr(output_file_name)}")
    if not isinstance(transactions, List):
        raise Exception(f"Internal error: parameter transactions is not of type List: {repr(transactions)}")

    output_file_path: Path = Path(output_dir_path) / Path(f"{output_file_prefix}{output_file_name}")
    if Path(output_file_path).exists():
        output_file_path.unlink()

    json_config: Dict[str, Any] = {
        Keyword.IN_HEADER.value: {},
        Keyword.OUT_HEADER.value: {},
        Keyword.INTRA_HEADER.value: {},
        _ASSETS: [],
        _EXCHANGES: [],
        _HOLDERS: [],
    }

    assets: Set[str] = set()
    holders: Set[str] = set()
    exchanges: Set[str] = set()
    for transaction in transactions:
        if is_fiat(transaction.asset):
            continue
        if isinstance(transaction, InTransaction):
            holders.add(transaction.holder)
            exchanges.add(transaction.exchange)
        elif isinstance(transaction, OutTransaction):
            holders.add(transaction.holder)
            exchanges.add(transaction.exchange)
        elif isinstance(transaction, IntraTransaction):
            holders.add(transaction.from_holder)
            holders.add(transaction.to_holder)
            exchanges.add(transaction.from_exchange)
            exchanges.add(transaction.to_exchange)
        else:
            raise Exception(f"Internal error: transaction is not a subclass of AbstractTransaction: {transaction}")
        assets.add(transaction.asset)

    for section_name in [Keyword.IN_HEADER, Keyword.OUT_HEADER, Keyword.INTRA_HEADER]:
        json_config[section_name.value] = global_configuration[section_name.value]

    if Keyword.UNKNOWN.value in assets:
        assets.remove(Keyword.UNKNOWN.value)
    if Keyword.UNKNOWN.value in holders:
        holders.remove(Keyword.UNKNOWN.value)
    if Keyword.UNKNOWN.value in exchanges:
        exchanges.remove(Keyword.UNKNOWN.value)
    json_config[_ASSETS] = list(assets)
    json_config[_HOLDERS] = list(holders)
    json_config[_EXCHANGES] = list(exchanges)

    with open(str(output_file_path), "w", encoding="utf-8") as output_file:
        json.dump(json_config, output_file, indent=4)
