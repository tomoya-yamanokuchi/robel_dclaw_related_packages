



def radius_to_string_mapping(radius: list):
    # assert len(mass) == 4
    radius_str_formatted = "{:.1e}".format(radius).replace('.', 'p')
    return radius_str_formatted
