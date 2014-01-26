========
Usage
========
.. code:: python

    ## Import rui
    from rui.rui import Component, System, World

    ## Define Components
    class Position(Component):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class Velocity(Component):
        def __init__(self, x, y):
            self.x = x
            self.y = y

    ## Define System
    class MovementSystem(System):
        def process(self, delta): ## This method is a minimal requirement
            entities = self.world.get_entities_by_components(Position, Velocity)

            for entity in entities:
                position = entity.getComponent(Position)
                velocity = entity.getComponent(Velocity)
                position.x += velocity.x * delta
                position.y += velocity.y * delta

    ## Create the world and set up Entities
    world = World()

    player = world.create_entity(tag='PLAYER') # This does not automatically add the entity to the world
                                   # You could also do player = Entity('PLAYER')
                                   # tag is completely optional, but it allows you to look up this entity later
    player.add_component(Position(0,0))
    player.add_component(Velocity(0,0))
    world.add_entity(player)
    
    world.add_system(MovementSystem())
    
    while True:
        ## Get Player Inputs
        player_by_tag = world.get_entity_by_tag('PLAYER') ## Get the entity by its tag
        world.process() ## The world will step through its motions
