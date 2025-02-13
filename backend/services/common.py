import datetime
import ee


def date_sequence(start, end, unit, date_format="YYYY-MM-dd", step=1):
    """Creates a date sequence.

    Args:
        start (str): The start date, e.g., '2000-01-01'.
        end (str): The end date, e.g., '2000-12-31'.
        unit (str): One of 'year', 'quarter', 'month' 'week', 'day', 'hour', 'minute', or 'second'.
        date_format (str, optional): A pattern, as described at http://joda-time.sourceforge.net/apidocs/org/joda/time/format/DateTimeFormat.html. Defaults to 'YYYY-MM-dd'.
        step (int, optional): The step size. Defaults to 1.

    Returns:
        ee.List: A list of date sequence.
    """

    def get_quarter(d):
        return str((int(d[5:7]) - 1) // 3 * 3 + 1).zfill(2)

    def get_monday(d):
        date_obj = datetime.datetime.strptime(d, "%Y-%m-%d")
        start_of_week = date_obj - datetime.timedelta(days=date_obj.weekday())
        return start_of_week.strftime("%Y-%m-%d")

    if unit == "year":
        start = start[:4] + "-01-01"
    elif unit == "month":
        start = start[:7] + "-01"
    elif unit == "quarter":
        start = start[:5] + get_quarter(start) + "-01"
    elif unit == "week":
        start = get_monday(start)

    start_date = ee.Date(start)
    end_date = ee.Date(end)

    if unit != "quarter":
        count = ee.Number(end_date.difference(start_date, unit)).toInt()
        num_seq = ee.List.sequence(0, count)
        if step > 1:
            num_seq = num_seq.slice(0, num_seq.size(), step)
        date_seq = num_seq.map(
            lambda d: start_date.advance(d, unit).format(date_format)
        )

    else:
        unit = "month"
        count = ee.Number(end_date.difference(start_date, unit)).divide(3).toInt()
        num_seq = ee.List.sequence(0, count.multiply(3), 3)
        date_seq = num_seq.map(
            lambda d: start_date.advance(d, unit).format(date_format)
        )

    return date_seq