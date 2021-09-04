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


    def generate_target( self ):
        sponsor = random.choice( self.sponsors )

        if 'target_pronoun' not in sponsor:
            sponsor['target_pronoun']            = 'they'
            sponsor['target_possessive_pronoun'] = 'they'
            sponsor['target_accusative_pronoun'] = 'they'
            pass

        # Let's assume that bigots are less often to use non-binary friendly pronouns
        gender = random.choices( ('male', 'female', 'non-binary' ), weights = (50, 50, 20), k = 1 )[0]

        if gender == 'male':
            random_person   = {
                'first_name'               : self.generator.first_name_male(),
                'last_name'                : self.generator.last_name_male(),
                'target_pronoun'           : 'he',
                'target_possessive_pronoun': 'his',
                'target_accusative_pronoun': 'him'
            }
            pass

        elif gender == 'female':
            random_person   = {
                'first_name'               : self.generator.first_name_female(),
                'last_name'                : self.generator.last_name_female(),
                'target_pronoun'           : 'she',
                'target_possessive_pronoun': 'her',
                'target_accusative_pronoun': 'her'
            }
            pass

        else:
            random_person   = {
                'first_name'               : self.generator.first_name_nonbinary(),
                'last_name'                : self.generator.last_name_nonbinary(),
                'target_pronoun'           : 'they',
                'target_possessive_pronoun': 'their',
                'target_accusative_pronoun': 'them'
            }
            pass

        return random.choices( (sponsor, random_person), weights = (30, 70), k = 1 )[0]




    def generate( self ):
        clinic_location = random.choice( self.counties_cities )


        args = {
            **self.generate_target(),
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


        args['possessive_pronoun'] = 'my'  if args['personal_pronoun'].lower() == 'i' else 'our'
        args['to_be']              = 'was' if args['personal_pronoun'].lower() == 'i' else 'were'


        stories = []
        for story_template in self.story_templates:
            story_line = random.choice( story_template )
            story      = story_line.format( **args )
            story      = story[0].upper() + story[1:]
            stories.append( story )

            # Well, consider using 'they', in the next sentences
            args['target_pronoun'] = random.choices( (args['first_name'], args['target_pronoun']), weights = (30, 70), k = 1 )[0]

            if args['personal_pronoun'].lower() != 'i':
                args['personal_pronoun'] = random.choices( (args['personal_pronoun'], 'we'), weights = (20, 80), k = 1 )[0]

            args['talking_synonym'] = random.choice( self.talking_synonyms )
            continue

        emojis = [ '🥱', '🙊' ]
        evidences = []
        for index, evidence_template in enumerate( self.evidence_templates ):
            evidence_line = random.choice( evidence_template )
            evidence      = evidence_line.format( **args )
            evidence      = evidence[0].upper() + evidence[1:]
            evidences.append( emojis[index] + ' ' + evidence )
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
