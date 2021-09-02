#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from faker                         import Faker
from faker.providers               import BaseProvider
from faker.providers.address.en_US import Provider as AddressProvider
from collections                   import OrderedDict
import ujson
import random
from sanic import Sanic
from sanic.response import text

class TexanProvider( AddressProvider ):
    states          = ('Texas',)
    states_abbr     = ('TX',)
    states_postcode = {'TX': (75503, 79999),}

    street_address_formats = (
        '{{building_number}} {{street_name}}',
        '{{building_number}} {{street_name}} {{secondary_address}}',
    )

    def city( self ):
        sampled = random.sample( self.counties_cities, 1 )[0]
        return self.generator.parse( sampled['city'] )

    def county( self ):
        sampled = random.sample( self.counties_cities, 1 )[0]
        return self.generator.parse( sampled['county'] )


    def generate( self ):
        story_template_1    = random.choice( self.story_templates_1 )
        story_template_2    = random.choice( self.story_templates_2 )
        evidence_template_1 = random.choice( self.evidence_templates_1 )
        clinic_location     = random.choice( self.counties_cities )


        args = {
            **random.choice( self.sponsors ),
            **random.choice( self.counties_cities ),
            'clinic_city'        : clinic_location['city'],
            'clinic_county'      : clinic_location['county'],
            'establishment'      : random.choice( self.establishments ),
            'family_member'      : random.choice( self.family_members ),
            'social_media'       : random.choice( self.social_medias ),
            'social_media_action': random.choice( self.social_media_actions ),
            'past'               : random.choice( self.past ),
            'future'             : random.choice( self.future ),
            'medium'             : random.choice( self.medium ),
        }

        story_1 = story_template_1.format(**args)
        args['first_name'] = random.choice( (args['first_name'], 'They') )
        story_2 = story_template_2.format( **args )
        evidence_1 = evidence_template_1.format( **args )

        result = f"""
--- Part 1: Story ---

{story_1}
{story_2}

--- Part 2: Evidence ---

{evidence_1}

--- Part 3: Doctor's address ---
{self.generator.street_address()}

--- Part 4: Details ---
City    : {clinic_location['city']}
County  : {clinic_location['county']}
State   : {self.generator.state()}
Zip Code: {self.generator.postcode_in_state()}
        """
        return result


with open( "./data.json", 'r' ) as file:
    data = ujson.load( file )

    for key in data.keys():
        setattr( TexanProvider, key, data[key] )
        continue

fake = Faker( {'en-US'} )
fake.add_provider( TexanProvider )

app = Sanic( 'adlib-generator')

@app.get( "/" )
async def generate( request ):
    return text( fake.generate() )

app.run(
    host  = '0.0.0.0',
    port  = os.environ.get('PORT') or 80,
    debug = True
)