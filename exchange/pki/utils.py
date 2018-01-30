
def pki_route(url):
    '''
    Rewrites a service url with prepended pki-routing path.
    :param url:
    :return: https://exchange:port/pki/<record-id>/url
    '''
    # parse out https:// and url encode 'url'
    # instead of exchange:port, use the current site url or something?
    # how is <record-id> incorporated? Right now we're just using
    # SSL_CONFIGS[0] because there's only one element in the list
    # but how would we know if we're using a different one???
    # Is there a setting which tells us which one we're using?
    # And then otherwise we have a model? But again, how do we know?

    # only want netloc of url and want it encoded
    pki_url = 'https://' + 'exchange:port' + '/pki/' + '0' + '/' + url
    return pki_url