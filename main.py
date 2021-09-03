#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ujson
import random
import click
from faker          import Faker
from sanic          import Sanic
from sanic.response import text
from adlib_provider import AdlibProvider

app  = Sanic( 'adlib-generator')
fake = Faker( {'en-US'} )

@app.get( "/" )
async def generate( request ):
    return text( fake.generate() )

@click.command()
@click.option( '--server', type = click.BOOL, is_flag = True )
def main( server ):
    with open( "./data.json", 'r' ) as file:
        data = ujson.load( file )

        for key in data.keys():
            setattr( AdlibProvider, key, data[key] )
            continue

    fake.add_provider( AdlibProvider )

    if server:
        app.run( host = '0.0.0.0', port = os.environ.get('PORT') or 80 )
        pass

    else:
        print( fake.generate() )
        pass


if __name__ == '__main__':
    main()