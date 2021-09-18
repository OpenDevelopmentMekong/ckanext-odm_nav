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


def check_date_period(data_dict, errors, period=366):
    """
    Check the dates from and two dates. Allowed period is only for 12 months period.
    :param data_dict: dict
    :param errors: dict
    :param period: int
    :return: errors
    """

    from_dt = parse(data_dict.get('from_dt'))
    to_dt = parse(data_dict.get('to_dt'))

    if from_dt >= to_dt:
        errors['from_dt'] = ["From date greater than to date"]
        return errors

    diff = to_dt - from_dt
    if diff.days > period:
        errors['from_dt'] = ["From date and To date period is greater than the "
                             "allowed period - {} days".format(str(period))]
        return errors

    return errors
