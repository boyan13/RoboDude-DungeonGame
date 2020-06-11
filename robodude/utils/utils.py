def get_proportional(current_size, target, width=True):
    '''
    Via passed size tuple and a target width or height,
    calculates the proportional second argument and returns it.
    '''
    if width:
        percentage = (target/float(current_size[0]))
        target_h = int((float(current_size[1])*float(percentage)))
        return target_h
    else:
        percentage = (target/float(current_size[1]))
        target_w = int((float(current_size[0])*float(percentage)))
        return target_w
