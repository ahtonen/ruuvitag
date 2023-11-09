import time

import boto3
import utils
from botocore.config import Config

database_name = utils.get_env_var("DATABASE")
table_name = utils.get_env_var("TABLE")
region = utils.get_env_var("AWS_REGION")


def _current_milli_time():
    return str(int(round(time.time() * 1000)))


def add_measure(measures, values, mname, mtype):
    measures.append(
        {
            "MeasureName": mname,
            "MeasureValueType": mtype,
            "MeasureValue": str(values[mname]),
        }
    )


def write_ruuvi_records(client, location, values):
    """
    Write ruuvi records from single sensor.

    Note that this is AWS single value type write.
    """
    current_time = _current_milli_time()

    dimensions = [
        {"Name": "location", "Value": location},
        {"Name": "mac", "Value": str(values["mac"])},
        {"Name": "data_format", "Value": str(values["data_format"])},
    ]

    common_attributes = {"Dimensions": dimensions, "Time": current_time}

    if len(values) == 0:
        return

    measures = []
    add_measure(measures, values, "humidity", "DOUBLE")
    add_measure(measures, values, "temperature", "DOUBLE")
    add_measure(measures, values, "pressure", "DOUBLE")
    add_measure(measures, values, "acceleration", "DOUBLE")
    add_measure(measures, values, "tx_power", "BIGINT")
    add_measure(measures, values, "battery", "BIGINT")
    add_measure(measures, values, "rssi", "BIGINT")

    if len(measures) > 0:
        try:
            print("Sending measures:", measures)
            result = client.write_records(
                DatabaseName=database_name,
                TableName=table_name,
                Records=measures,
                CommonAttributes=common_attributes,
            )
            print(
                "WriteRecords Status: [%s]"
                % result["ResponseMetadata"]["HTTPStatusCode"]
            )
        except client.exceptions.RejectedRecordsException as err:
            print("RejectedRecords: ", err)
            for rr in err.response["RejectedRecords"]:
                print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
                print("Other records were written successfully. ")
        except Exception as err:
            print("Error:", err)
    else:
        print("No measures to send")


if __name__ == "__main__":
    """
    Write single measurements to AWS Timestream.
    """
    location = "sauna"
    values = utils.ruuvi_measurements[location]

    session = boto3.Session()

    # Recommended Timestream write client SDK configuration:
    #  - Set SDK retry count to 10.
    #  - Use SDK DEFAULT_BACKOFF_STRATEGY
    #  - Set RequestTimeout to 20 seconds .
    #  - Set max connections to 5000 or higher.
    # write_client = session.client('timestream-write', config=Config(region_name=region, read_timeout=20, max_pool_connections = 5000, retries={'max_attempts': 10}))
    # query_client = session.client('timestream-query', config=Config(region_name=region))
    write_client = session.client(
        "timestream-write",
        config=Config(
            region_name=region,
            read_timeout=20,
            max_pool_connections=5000,
            retries={"max_attempts": 10},
        ),
    )

    write_ruuvi_records(write_client, location, values)
