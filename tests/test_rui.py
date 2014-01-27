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
                            UnmanagedEntityError, UnmanagedSystemError,
                            NonUniqueTagError, DeadEntityError)


class Counter(Component):
    def __init__(self, count):
        self.count = count


class Empty(Component):
    def __init__(self):
        pass


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
        replaceCounter = Counter(1)
        entity.add_component(counter)
        self.assertTrue(counter in entity.get_components())
        getCounter = entity.get_component(Counter)
        self.assertEqual(counter, getCounter)
        self.assertEqual(getCounter.count, 0)
        entity.add_component(replaceCounter)
        self.assertTrue(counter in entity.get_components())
        getCounter = entity.get_component(Counter)
        self.assertEqual(replaceCounter, getCounter)
        self.assertEqual(getCounter.count, 1)

    def test_get_entites_by_components(self):
        entity = self.world.create_entity()
        entity.add_component(Counter(0))
        entity.add_component(Empty())
        empty_entity = self.world.create_entity()
        empty_entity.add_component(Empty())
        self.world.add_entity(entity)
        self.world.add_entity(empty_entity)

        partial_entities = self.world.get_entities_by_components(Counter)
        self.assertEqual(len(partial_entities), 1)

        full_entities = self.world.get_entities_by_components(Counter, Empty)
        self.assertEqual(len(full_entities), 1)
        self.assertEqual(full_entities, partial_entities)

        empty_entities = self.world.get_entities_by_components(Empty)
        self.assertEqual(len(empty_entities), 2)
        self.assertTrue(empty_entity in empty_entities)

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

    def test_kill_entity(self):
        entity = self.world.create_entity('KILL')
        self.world.add_entity(entity)
        self.assertTrue(entity in self.world.get_entities())
        entity.kill()
        self.assertFalse(entity in self.world.get_entities())

        entity = self.world.create_entity('KILL')
        self.world.add_entity(entity)
        self.assertTrue(entity in self.world.get_entities())
        self.world.remove_entity(entity)
        self.assertFalse(entity in self.world.get_entities())
        with self.assertRaises(DeadEntityError):
            entity.kill()

    ## Testing Systems
    def test_add_system(self):
        entity = self.world.create_entity()
        entity.add_component(Counter(0))
        self.world.add_entity(entity)
        count_system = CountSystem()
        self.world.add_system(count_system)
        count_system.process(1)
        self.assertEqual(entity.get_component(Counter).count, 1)
        self.world.process()
        self.assertEqual(entity.get_component(Counter).count, 2)

    def test_remove_system(self):
        entity = self.world.create_entity()
        entity.add_component(Counter(0))
        self.world.add_entity(entity)
        count_system = CountSystem()
        self.world.add_system(count_system)
        self.world.process()
        self.assertEqual(entity.get_component(Counter).count, 1)
        self.world.remove_system(count_system)
        self.world.process()
        self.assertEqual(entity.get_component(Counter).count, 1)

    ## Test Exceptions
    def test_duplicate_entity_error(self):
        entity = self.world.create_entity()
        self.world.add_entity(entity)
        with self.assertRaises(DuplicateEntityError):
            self.world.add_entity(entity)

    def test_duplicate_system_error(self):
        count_system = CountSystem()
        duplicateCountSystem = CountSystem()
        self.world.add_system(count_system)
        with self.assertRaises(DuplicateSystemError):
            self.world.add_system(count_system)
            self.world.add_system(duplicateCountSystem)

    def test_unmanaged_entity_error(self):
        entity = self.world.create_entity()
        with self.assertRaises(UnmanagedEntityError):
            self.world.register_entity_to_group(entity, 'GROUP')
        self.world.add_entity(entity)
        self.world.register_entity_to_group(entity, 'GROUP')

    def test_unmanaged_system_error(self):
        count_system = CountSystem()
        with self.assertRaises(UnmanagedSystemError):
            self.world.remove_system(count_system)
        self.world.add_system(count_system)
        self.world.remove_system(count_system)

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
