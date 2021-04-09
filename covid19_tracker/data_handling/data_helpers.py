def LKname_to_ags(ags_dict, lk_name):
    for ags in ags_dict.keys():
        if ags_dict[ags]["name"] == lk_name:
            return ags