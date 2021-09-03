#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
from faker.providers               import BaseProvider
from faker.providers.address.en_US import Provider as AddressProvider
from collections                   import OrderedDict


class AdlibProvider( AddressProvider ):
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
        clinic_location = random.choice( self.counties_cities )
        sponsor         = random.choice( self.sponsors )
        random_person   = {
            'first_name': self.generator.first_name(),
            'last_name' : self.generator.last_name(),
        }

        args = {
            **random.choices( (sponsor, random_person), weights = (30, 70), k = 1 )[0],
            **random.choice( self.counties_cities ),
            'clinic_city'  : clinic_location['city'],
            'clinic_county': clinic_location['county'],
        }

        # Load all the data that's a key => list of items pair
        for key, value in AdlibProvider.__dict__.items():
            if key.endswith( 'templates' ):
                continue

            if type( value ) is list:
                args[ key[:len(key)-1] ] = random.choice( value )


        stories = []
        for story_template in self.story_templates:
            story_line = random.choice( story_template )
            story      = story_line.format( **args )
            stories.append( story )

            # Well, consider using 'they', in the next sentences
            args['first_name'] = random.choices( (args['first_name'], 'they'), weights = (70, 30), k = 1 )[0]

            if 'and' in args['personal_pronoun']:
                args['personal_pronoun'] = random.choices( (args['personal_pronoun'], 'we'), weights = (30, 70), k = 1 )[0]

            continue

        evidences = []
        for evidence_template in self.evidence_templates:
            evidence_line = random.choice( evidence_template )
            evidence      = evidence_line.format( **args )
            evidences.append( evidence )
            continue


        clinics = []
        for clinic_template in self.clinic_templates:
            clinic_line = random.choice( clinic_template )
            clinic      = clinic_line.format( street  = self.generator.street_address(),
                                              city    = clinic_location['city'],
                                              county  = clinic_location['county'],
                                              state   = 'TX',
                                              zipcode = self.generator.postcode_in_state() )
            clinics.append( clinic )
            continue

        stories   = '\n'.join( stories )
        evidences = '\n'.join( evidences )
        clinics   = '\n'.join( clinics )

        result = f"""
--- Part 1: Story ---

{stories}

--- Part 2: Evidence ---

{evidences}

--- Part 3: Doctor's address ---

{clinics}

--- Part 4: Details ---
City    : {args['city']}
County  : {args['county']}
State   : {self.generator.state()}
Zip Code: {self.generator.postcode_in_state()}
"""
        return result
