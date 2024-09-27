

def convert_to_min(value):
    if ':' in value:
        hour, minute = value.split(':')
        hour = int(hour)
        minute = int(minute)
        minute = (hour * 60) + minute
        return minute
    else:
        minute = int(value)
        return minute


if __name__ == '__main__':
    value = input('Digita algo')
    convert_to_min(value)
