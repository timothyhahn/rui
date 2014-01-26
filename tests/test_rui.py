#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_rui
----------------------------------

Tests for `rui` module.
"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from rui.rui import Component, System, World
from rui.exceptions import (DuplicateEntityError, DuplicateSystemError,
                            UnmanagedEntityError, NonUniqueTagError)


class Counter(Component):
    def __init__(self, count):
        self.count = count


class CountSystem(System):
    def process(self, delta):
        entities = self.world.get_entities_by_components(Counter)

        for entity in entities:
            entity.get_component(Counter).count += (1 * delta)


class TestRui(unittest.TestCase):

    def setUp(self):
        self.world = World()

    ## Testing Components
    def test_add_component(self):
        entity = self.world.create_entity()
        counter = Counter(0)
        entity.add_component(counter)
        self.assertTrue(counter in entity.get_components())
        getCounter = entity.get_component(Counter)
        self.assertEqual(counter, getCounter)
        self.assertEqual(getCounter.count, 0)

    ## Testing Entities
    def test_add_entity(self):
        entity = self.world.create_entity()
        self.world.add_entity(entity)
        self.assertTrue(entity in self.world.get_entities())

    def test_entity_tag(self):
        noTagEntity = self.world.create_entity()
        tagEntity = self.world.create_entity('TAG')
        self.world.add_entities(noTagEntity, tagEntity)
        self.assertNotEqual(noTagEntity, self.world.get_entity_by_tag('TAG'))
        self.assertEqual(tagEntity, self.world.get_entity_by_tag('TAG'))

    def test_groups(self):
        inGroupEntity = self.world.create_entity()
        inGroupEntity2 = self.world.create_entity()
        notInGroupEntity = self.world.create_entity()
        self.world.add_entity(inGroupEntity)
        self.world.add_entity(inGroupEntity2)
        self.world.add_entity(notInGroupEntity)
        self.world.register_entity_to_group(inGroupEntity, 'GROUP')
        self.world.register_entity_to_group(inGroupEntity2, 'GROUP')
        group = self.world.get_group('GROUP')
        self.assertTrue(inGroupEntity in group)
        self.assertTrue(inGroupEntity2 in group)
        self.assertFalse(notInGroupEntity in group)

    ## Testing Systems
    def test_add_system(self):
        entity = self.world.create_entity()
        entity.add_component(Counter(0))
        entity.add_component(Counter(0))
        self.world.add_entity(entity)
        countSystem = CountSystem()
        self.world.add_system(countSystem)
        countSystem.process(1)
        self.assertEqual(entity.get_component(Counter).count, 1)
        self.world.process()
        self.assertEqual(entity.get_component(Counter).count, 2)

    ## Test Exceptions
    def test_duplicate_entity_error(self):
        entity = self.world.create_entity()
        self.world.add_entity(entity)
        with self.assertRaises(DuplicateEntityError):
            self.world.add_entity(entity)

    def test_duplicate_system_error(self):
        countSystem = CountSystem()
        duplicateCountSystem = CountSystem()
        self.world.add_system(countSystem)
        with self.assertRaises(DuplicateSystemError):
            self.world.add_system(countSystem)
            self.world.add_system(duplicateCountSystem)

    def test_unmanaged_entity_error(self):
        entity = self.world.create_entity()
        with self.assertRaises(UnmanagedEntityError):
            self.world.register_entity_to_group(entity, 'GROUP')
        self.world.add_entity(entity)
        self.world.register_entity_to_group(entity, 'GROUP')

    def test_non_unique_tag_error(self):
        entity = self.world.create_entity('TAG')
        self.world.add_entity(entity)
        nonUniqueEntity = self.world.create_entity('TAG')
        otherEntity = self.world.create_entity('FAKE')
        self.world.add_entity(otherEntity)

        with self.assertRaises(NonUniqueTagError):
            self.world.add_entity(nonUniqueEntity)
            self.world.get_entity_by_tag('FAKE').set_tag('TAG')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()