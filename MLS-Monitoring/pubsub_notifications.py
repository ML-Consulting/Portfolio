import json
import logging
from google.cloud import pubsub_v1
from config import config


def replay_pubsub_messages() -> list:
    """
    Retrieves messages from a Pub/Sub subscription that were published in the last 48 hours, processes them, and returns a list of message dictionaries.
    """

    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(config.project_id, config.pubsub_id)

    try:
        response = subscriber.pull(request={"subscription": sub_path, "max_messages": 100})
    except Exception as e:
        logging.error(f"Error pulling messages from Pub/Sub: {e}")
        return []

    li_msg = []   

    for msg in response.received_messages:

        try:
            msg_data = json.loads(msg.message.data.decode("utf-8"))
            proto = msg_data.get("protoPayload", {})
            status = proto.get("status", {})
            
            logging.debug(f"Processing message: {msg_data}")
            
            msg_dict = {
                "message_id": msg_data["insertId"],
                "severity": msg_data["severity"],
                "text_payload": (
                                msg_data.get("textPayload")
                                or status.get("message")
                                or json.dumps(msg_data.get("jsonPayload") or msg_data.get("protoPayload", {}))
                            ),
                "publish_time": config.time_util_now(msg_data["timestamp"])
            }
            li_msg.append(msg_dict)

            # Ack them so they aren't redelivered again
            subscriber.acknowledge(request={"subscription": sub_path, "ack_ids": [msg.ack_id]})
        except Exception as e:
            logging.error(f"Error processing message {msg.message.data}: {e}")

    return li_msg
