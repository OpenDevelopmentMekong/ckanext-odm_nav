from dateutil.parser import parse


def validate_date(key, data_dict, errors):
    """
    Validate the date format
    :param key: from_dt or to_dt
    :param data_dict: dict
    :param errors: dict
    :return: raises error
    """
    try:
        if not data_dict.get(key):
            raise ValueError
    except ValueError:
        errors[key] = ["Not a valid date"]
        return errors
    parse(data_dict.get(key))
    return None


def check_date_period(data_dict, errors):
    """
    Check the dates from and two dates. Allowed period is only for 6 months period.
    :param data_dict: dict
    :param errors: dict
    :return: errors
    """

    from_dt = parse(data_dict.get('from_dt'))
    to_dt = parse(data_dict.get('to_dt'))

    if from_dt >= to_dt:
        errors['from_dt'] = ["From date greater than to date"]
        return errors

    return errors
