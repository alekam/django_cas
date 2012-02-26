
def attr_filler(user, attrib):
    """Fill user attributes from CAS response"""
    if attrib is None:
        return user
    changed = False
    ATTRIB_TAG = '%sattribute' % '{http://www.yale.edu/tp/cas}'
    for attr in attrib[0]:
        if attr.tag != ATTRIB_TAG:
            continue
        if attr.attrib['name'] in ['is_staff', 'is_active', 'is_superuser', ]:
            old_val = getattr(user, attr.attrib['name'])
            new_val = attr.attrib['value'].strip() == 'True'
            if old_val != new_val:
                setattr(user, attr.attrib['name'], new_val)
                changed = True
        elif attr.attrib['name'] in ['email', 'first_name', 'last_name']:
            old_val = getattr(user, attr.attrib['name'])
            new_val = attr.attrib['value'].strip()
            if old_val != new_val:
                setattr(user, attr.attrib['name'], new_val)
                changed = True
    if changed:
        user.save()
    return user
