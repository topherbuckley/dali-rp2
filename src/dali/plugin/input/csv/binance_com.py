# Copyright 2022 macanudo527
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

# Autoinvest CSV Format: timestamp UTC, base asset symbol, quote asset amount + symbol, trading fee (in quote asset), 
#    base asset amount + symbol, source of funds
# Note: file comes as .xlsx, and then needs to be saved as CSV.

# Betheth CSV format: timestamp UTC, quote asset symbol (ETH), base asset symbol (BETH), amount, status

import logging
from csv import reader
from typing import Dict, List, Optional

from rp2.logger import create_logger
from rp2.rp2_decimal import RP2Decimal, ZERO

from dali.abstract_input_plugin import AbstractInputPlugin
from dali.abstract_transaction import AbstractTransaction
from dali.configuration import Keyword
from dali.in_transaction import InTransaction
from dali.intra_transaction import IntraTransaction
from dali.out_transaction import OutTransaction

class InputPlugin(AbstractInputPlugin):

    __BINANCE_COM: str = "Binance.com"
    __BINANCE_COM_CSV: str = "Binance.com CSV"

    __TIMESTAMP_INDEX: int = 0
    __AUTO_BASE_SYMBOL: int = 1
    __AUTO_QUOTE_AMOUNT_SYMBOL: int = 2
    __AUTO_TRADING_FEE: int = 3
    __BETHETH_AMOUNT: int = 3
    __AUTO_BASE_AMOUNT_SYMBOL: int = 4
    __FUND_SOURCE: int = 5

    __DELIMITER: str = ","

    def __init__(
        self,
        account_holder: str,
        autoinvest_csv_file: Optional[str] = None,
        betheth_csv_file: Optional[str] = None,
        native_fiat: Optional[str] = None,
    ) -> None:

        super().__init__(account_holder=account_holder, native_fiat=native_fiat)
        self.__autoinvest_csv_file: str = autoinvest_csv_file
        self.__betheth_csv_file: str = betheth_csv_file
        self.__logger: str = logging.Logger = create_logger(f"{self.__BINANCE_COM_CSV}/{self.account_holder}")

    def load(self) -> List[AbstractTransaction]:
        result: List[AbstractTransaction] = []

        if self.__autoinvest_csv_file:
            result += self.parse_autoinvest_file(self.__autoinvest_csv_file)

        if self.__betheth_csv_file:
            result += self.parse_betheth_file(self.__betheth_csv_file)

        return result

    def parse_autoinvest_file(self, file_path: str) -> List[AbstractTransaction]:
        result: List[AbstractTransaction] = []

        with open(file_path, encoding="utf-8") as csv_file:
            lines = reader(file_path)

            header = next(lines)
            self.__logger.debug("Header: %s", header)
            for line in lines:
                raw_data: str = self.__DELIMITER.join(line)
                self.__logger.debug("Transaction: %s", raw_data)


                result.append(
                    InTransaction(
                        plugin=self.__BINANCE_COM_CSV,
                        unique_id=Keyword.UNKNOWN.value,
                        raw_data=raw_data,
                        timestamp=f"{line[self.__TIMESTAMP_INDEX]} -00:00",
                        asset=line[self.__AUTO_BASE_SYMBOL],
                        exchange=self.__BINANCE_COM,
                        holder=self.account_holder,
                        transaction_type=Keyword.BUY.value,
                        spot_price=Keyword.UNKNOWN.value,
                        crypto_in=(line[self.__AUTO_BASE_AMOUNT_SYMBOL]).split()[0],
                        fiat_fee=ZERO,
                        notes=f"Funding from {line[self.__FUND_SOURCE]}",
                    )
                )

                quote_asset_symbol: str = line[self.__AUTO_QUOTE_AMOUNT_SYMBOL].split()[1]
                quote_asset_amount: str = line[self.__AUTO_QUOTE_AMOUNT_SYMBOL].split()[0]
                crypto_out_with_fee: RP2Decimal = RP2Decimal(quote_asset_amount) + RP2Decimal(line[self.__AUTO_TRADING_FEE]) 
                result.append(
                    OutTransaction(
                        plugin=self.__BINANCE_COM_CSV,
                        unique_id=Keyword.UNKNOWN.value,
                        raw_data=raw_data,
                        timestamp=f"{line[self.__TIMESTAMP_INDEX]} -00:00",
                        asset=quote_asset_symbol,
                        exchange=self.__BINANCE_COM,
                        holder=account_holder,
                        transaction_type=Keyword.SELL.value,
                        spot_price=Keyword.UNKNOWN.value,
                        crypto_out_no_fee=quote_asset_amount,
                        crypto_out_with_fee=crypto_out_with_fee,
                        crypto_fee=line[self.__AUTO_TRADING_FEE],
                        notes=f"Funding from {line[self.__FUND_SOURCE]}",
                    )
                )

        def parse_betheth_file(self, file_path: str) -> List[AbstractTransaction]:
        result: List[AbstractTransaction] = []

        with open(file_path, encoding="utf-8") as csv_file:
            lines = reader(file_path)

            header = next(lines)
            self.__logger.debug("Header: %s", header)
            for line in lines:
                raw_data: str = self.__DELIMITER.join(line)
                self.__logger.debug("Transaction: %s", raw_data)


                result.append(
                    InTransaction(
                        plugin=self.__BINANCE_COM_CSV,
                        unique_id=Keyword.UNKNOWN.value,
                        raw_data=raw_data,
                        timestamp=f"{line[self.__TIMESTAMP_INDEX]} -00:00",
                        asset="BETH",
                        exchange=self.__BINANCE_COM,
                        holder=self.account_holder,
                        transaction_type=Keyword.BUY.value,
                        spot_price=Keyword.UNKNOWN.value,
                        crypto_in=line[self.__BETHETH_AMOUNT],
                        fiat_fee=ZERO,
                        notes="Conversion from BETH -> ETH",
                    )
                )
 
                result.append(
                    OutTransaction(
                        plugin=self.__BINANCE_COM_CSV,
                        unique_id=Keyword.UNKNOWN.value,
                        raw_data=raw_data,
                        timestamp=f"{line[self.__TIMESTAMP_INDEX]} -00:00",
                        asset=quote_asset_symbol,
                        exchange=self.__BINANCE_COM,
                        holder=account_holder,
                        transaction_type=Keyword.SELL.value,
                        spot_price=Keyword.UNKNOWN.value,
                        crypto_out_no_fee=line[self.__BETHETH_AMOUNT],
                        crypto_out_with_fee=line[self.__BETHETH_AMOUNT],
                        crypto_fee=ZERO,
                        notes="Conversion from BETH -> ETH",
                    )
                )
