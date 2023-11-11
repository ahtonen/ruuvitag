import logging
import time

import boto3

from utils import get_env_var

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

country = get_env_var("COUNTRY")
city = get_env_var("CITY")
place = get_env_var("PLACE")
database_name = get_env_var("DATABASE")
table_name = get_env_var("TABLE")


def _current_milli_time():
    return str(int(round(time.time() * 1000)))


def add_measure(measures: list, values: dict, mname: str, mtype: str):
    """
    Add measurement in AWS Timestream multi measurement format.
    """
    if (mtype == "DOUBLE" or mtype == "BIGINT") and (values[mname] is None):
        logger.warning(
            "Trying to write 'None' to AWS Timestream: (%s, %s, %s). Skipping this measurement...",
            mname,
            mtype,
            values[mname],
        )
        return

    measures.append(
        {
            "Name": mname,
            "Type": mtype,
            "Value": str(values[mname]),
        }
    )


def write_ruuvi_record(
    write_client: boto3.Session.client,
    location: str,
    measurement: dict,
):
    """
    Write ruuvi records from single sensor.
    """
    current_time = _current_milli_time()

    common_attributes = {
        "Dimensions": [
            {"Name": "country", "Value": country},
            {"Name": "city", "Value": city},
            {"Name": "place", "Value": place},
            {"Name": "location", "Value": location},
            {"Name": "sensor_mac", "Value": str(measurement["mac"])},
            {"Name": "data_format", "Value": str(measurement["data_format"])},
        ],
        "MeasureName": "ruuvitag",
        "MeasureValueType": "MULTI",
    }

    if not measurement:
        logger.warning("Empty measurement: %s", measurement)
        return

    measures = []
    add_measure(measures, measurement, "humidity", "DOUBLE")
    add_measure(measures, measurement, "temperature", "DOUBLE")
    add_measure(measures, measurement, "pressure", "DOUBLE")
    add_measure(measures, measurement, "acceleration", "DOUBLE")
    add_measure(measures, measurement, "tx_power", "BIGINT")
    add_measure(measures, measurement, "battery", "BIGINT")
    add_measure(measures, measurement, "rssi", "BIGINT")

    records = [{"Time": current_time, "MeasureValues": measures}]

    if len(measures) > 0:
        try:
            logger.debug("Sending records: %s", records)
            result = write_client.write_records(
                DatabaseName=database_name,
                TableName=table_name,
                Records=records,
                CommonAttributes=common_attributes,
            )
            logger.info(
                "WriteRecords status for sensor %s: [%i]",
                str(measurement["mac"]),
                result["ResponseMetadata"]["HTTPStatusCode"],
            )
        except write_client.exceptions.RejectedRecordsException as err:
            logger.warning("RejectedRecords: %s", err)

            for rr in err.response["RejectedRecords"]:
                logger.warning(
                    "Rejected Index %s: %s", str(rr["RecordIndex"]), rr["Reason"]
                )
                logger.warning("Other records were written successfully.")

        except Exception as err:
            logger.error("Error: %s", err)
            logger.error("Records: %s", records)
    else:
        logger.warning("No measures to send")
