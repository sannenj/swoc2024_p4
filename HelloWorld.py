import functools
import operator

import grpc
import numpy as np
import asyncio
import player_pb2
import player_pb2_grpc

playerIdentifier = ""

MY_NAME = 'Tommie'

def calc_dist(p1, p2):
    delta = map(lambda x, y: abs(x - y), p1, p2)
    return functools.reduce(operator.add, delta, 0)


class Snake:
    Head = []
    Segments = []
    Length = 1
    Name = ""
    KidCount = 0
    New = False
    Hunt = None
    Target = None

    def __init__(self, address, name):
        print("creating new snake '{}' at {}".format(name, address))
        self.Head = address
        self.Segments = [address]
        self.Name = name
        self.New = True
        self.Hunt = None
        self.Target = None
        #print("snake is finished: " + name)

    def debug_print(self):
        print('{}: len={}, head={}'.format(self.Name, self.Length, self.Head))
        for seg in self.Segments:
            print('  {}'.format(seg))


class Cell:
    Address = []
    HasFood = False
    Player = ''

    def __init__(self):
        pass


class Food:
    Address = []
    Claims = 0

    def __init__(self, address):
        self.Address = list(address)


class GameState:
    Cells = []
    Dimensions = []
    Snakes = []
    Foods = []
    OtherSnakes = []

    def __init__(self, dims, startAddress, playerName):
        self.SaveAddress = startAddress
        self.Snakes.append(Snake(address=startAddress, name=playerName))
        self.Dimensions = dims
        totalCells = np.prod(dims)
        self.Cells = np.array([None]*totalCells).reshape(dims)
    
    def checkBounds(self, lst, indices):
        if indices.any():
            if indices[0] < 0:
                return False
            if len(lst) <= indices[0]:
                return False
            return self.checkBounds(lst[indices[0]], indices[1:])
        return True
    
    def getCell(self, lst, indices, address):
        if indices:
            return self.getCell(lst[indices[0]], indices[1:], address)
        if lst is None:
            lst = Cell()
            lst.Address = address
        return lst
    
    def getCell(self, address):
        cell = self.Cells[tuple(address)]
        if cell is None:
            cell = Cell()
            cell.Address = address
            cell.HasFood = False
            cell.Player = ''
            self.Cells[tuple(address)] = cell
        return cell

    def update_other_snake_move(self, player, address, grow):
        for snake in self.OtherSnakes:
            if snake.Name == player and calc_dist(list(snake.Head), list(address)) == 1:
                snake.Head = address
                snake.Segments.append(address)
                if grow:
                    snake.Length += 1
                    #print('OTHER {} GROW to {}'.format(snake.Name, snake.Head))
                else:
                    #print('OTHER {} move to {}'.format(snake.Name, snake.Head))
                    snake.Segments = snake.Segments[1:]
                return
        # Not adjacent to exiting head, assume new. Not bothering now to find/guess the full length
        #print('OTHER {} NEW at {}'.format(player, address))
        self.OtherSnakes.append(Snake(address, player))

    def prune_other_snakes(self):
        for snake in self.OtherSnakes:
            invalid_segments = 0
            for seg in snake.Segments:
                if self.getCell(seg).Player != snake.Name:
                    #print('OTHER {} {} segment {} is dead'.format(snake.Name, snake.Head, seg))
                    invalid_segments += 1
                else:
                    break
            #if invalid_segments > 0:
            #    print('OTHER {} prune {} from {}'.format(snake.Name, invalid_segments, snake.Head))
            snake.Segments = snake.Segments[invalid_segments:]
            snake.Length -= invalid_segments
        for snake in self.OtherSnakes[:]:
            if snake.Length == 0:
                #print('OTHER {} DIED at {}'.format(snake.Name, snake.Head))
                self.OtherSnakes.remove(snake)

    def set_state(self, initial_state):
        for updatedCell in initial_state.updatedCells:
            cell = self.getCell(updatedCell.address)
            if updatedCell.player and updatedCell.player != MY_NAME:
                self.update_other_snake_move(updatedCell.player, updatedCell.address, grow=True)
            cell.HasFood = updatedCell.foodValue > 0
            cell.Player = updatedCell.player
            if cell.HasFood:
                self.Foods.append(Food(updatedCell.address))

    def update(self, gameUpdate):
        for updatedCell in gameUpdate.updatedCells:
            #print('    update: {}: food={}, player={}'.format(updatedCell.address, updatedCell.foodValue, updatedCell.player))
            cell = self.getCell(updatedCell.address)
            if updatedCell.player and updatedCell.player != MY_NAME:
                self.update_other_snake_move(updatedCell.player, updatedCell.address, grow=cell.HasFood)
            cell.HasFood = updatedCell.foodValue > 0
            cell.Player = updatedCell.player
            if not cell.HasFood:
                for food in self.Foods:
                    if list(updatedCell.address) == food.Address:
                        print('remove food {}'.format(updatedCell.address))
                        self.Foods.remove(food)
                        break
        for name in gameUpdate.removedSnakes:
            print("  update: snake removed '{}'".format(name))
        for snake in self.Snakes[:]:
            if MY_NAME + ':' + snake.Name in gameUpdate.removedSnakes:
                print("SNAKE REMOVED: {} {}".format(snake.Name, snake.Head))
                self.Snakes.remove(snake)
                head_cell = self.getCell(snake.Head)
                if head_cell.Player == MY_NAME:
                    head_cell.Player = ''  # In case of claim, this ws claimed, but will not be updated by server
                if snake.Hunt:
                    snake.Hunt.Hunt = None  # other snake is not hunted anymore
            elif self.getCell(snake.Head).Player != MY_NAME:
                # Died... or saved!
                print("***** SNAKE is not in expected cell, removing: {} {}", snake.Name, snake.Head)
                self.Snakes.remove(snake)
        self.prune_other_snakes()
        for food in self.Foods:
            food.Claims = 0

    def nearest_food(self, snake):
        nearest = Food(self.SaveAddress)  # alternative target
        too_long = snake.Length >= 8  # prefer to save if too long
        nearest_dist = 5 if too_long else 10000000000  # when saving, allow small detours for food
        for food in self.Foods:
            penalty = 2 * food.Claims
            dist = calc_dist(list(snake.Head), food.Address) + penalty
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = food
        return nearest

    def get_next_address_for_hunt(self, snake):
        address = list(snake.Head)
        if address == snake.Target:
            print("Hunter reached target, but no hit...")
            snake.Target = None
        if snake.Target:  # pinned target
            target = snake.Target
        else:
            target = list(snake.Hunt.Head)
            # if in guaranteed range, pin target
            if calc_dist(target, address) <= snake.Hunt.Length:
                snake.Target = target
        i_largest_delta = 0
        largest_delta = 0
        for i in range(len(target)):
            delta = abs(target[i] - address[i])
            if delta > largest_delta:
                largest_delta = delta
                i_largest_delta = i
        next_addr = address
        change = np.sign(target[i_largest_delta] - snake.Head[i_largest_delta])
        next_addr[i_largest_delta] += change
        if self.getCell(next_addr).Player == MY_NAME:
            print("Hunter blocked by myself!")
            return self.getNextAddressRandom(snake.Head)
        else:
            print('{}: {} -> {}, HUNT'.format(snake.Name, str(address), str(next_addr)))
            return next_addr

    def get_next_address_for_food(self, snake):
        address = snake.Head
        target = self.nearest_food(snake)
        for i in range(len(address)):
            next_addr = list(address)
            change = np.sign(target.Address[i] - address[i])
            next_addr[i] += change
            if change != 0 and not self.getCell(next_addr).Player:
                target_is_save = target.Address == list(self.SaveAddress)
                print('{}: {} -> {}, target {} {}'.format(snake.Name, str(address), str(next_addr),
                                                          str(target.Address), 'save' if target_is_save else ''))
                if next_addr == list(self.SaveAddress):
                    print(" *** SAVE! *** {}".format(snake.Name))
                target.Claims += 1
                return next_addr
        print('{}: {}, target {} BLOCKED, target="{}"'.format(snake.Name, str(address), str(target.Address), self.getCell(target.Address).Player))
        # all direct routes blocked, do random (non-blocked) move
        return self.getNextAddressRandom(address)

    def getNextAddressRandom(self, address):
        for _ in range(100):
            newaddr = np.copy(address)
            dim = np.random.randint(len(self.Dimensions))
            dir = np.random.randint(2)
            if dir > 0:
                newaddr[dim] += 1
            else:    
                newaddr[dim] -= 1
            if self.checkBounds(self.Cells, newaddr):
                cell = self.getCell(newaddr)
                if not cell.Player:
                    print('{}: RANDOM to {}'.format(str(address), str(newaddr)))
                    return newaddr
        return []

    def getMoves(self):
        moves = []
        for snake in self.Snakes:
            if snake.New:
                snake.New = False
            else:
                if snake.Hunt and not self.getCell(snake.Hunt.Head).Player:
                    print("{}: Target gone, stop hunt", snake.Name)
                    snake.Hunt = None
                if snake.Hunt:
                    nextLocation = self.get_next_address_for_hunt(snake)
                else:
                    nextLocation = self.get_next_address_for_food(snake)
                if len(nextLocation) > 0:
                    snake.Head = nextLocation
                    cell = self.getCell(nextLocation)
                    snake.Segments.append(nextLocation)
                    if cell.HasFood:
                        snake.Length += 1
                        print('EAT! {}'.format(nextLocation))
                        #self.Foods.remove(list(nextLocation))
                    else:
                        snake.Segments = snake.Segments[1:]
                    cell.Player = MY_NAME  # claim space, so no other snakes will try to move here too
                    moves.append(player_pb2.Move(playerIdentifier=playerIdentifier, snakeName=snake.Name, nextLocation=nextLocation))
        return moves

    def split_snake(self, snake, cut_point):
        #print("old snake:")
        #snake.debug_print()

        # split the snake
        snake.Length -= cut_point
        snake.KidCount += 1
        new_head = snake.Segments[cut_point - 1]
        #print("create new head:", new_head)
        new_snake = Snake(address=new_head, name=snake.Name + "." + str(snake.KidCount))
        new_snake.Segments = snake.Segments[0:cut_point]
        new_snake.Length = len(new_snake.Segments)
        snake.Segments = snake.Segments[cut_point:]
        self.Snakes.append(new_snake)
        #print("new snake:")
        #new_snake.debug_print()
        print("old snake after split:")
        snake.debug_print()

        # move the new (tail) snake
        new_addr = self.getNextAddressRandom(new_head)
        if len(new_addr) > 0:
            new_snake.Head = new_addr
            new_snake.Segments.append(new_snake.Head)
            #print("move new head:", new_snake.Head)
            cell = self.getCell(address=new_snake.Head)
            if cell.HasFood:
                new_snake.Length += 1
                print('EAT by new snake! {}'.format(new_snake.Head))
            else:
                new_snake.Segments = new_snake.Segments[1:]
        print("new snake after move:")
        new_snake.debug_print()
        return new_snake

    def getSplits(self):
        splits = []

        # start offensive hunts
        for other in self.OtherSnakes:
            if other.Length >= 6 and not other.Hunt:
                best_snake = None
                best_dist = 10000000
                for snake in self.Snakes:
                    if snake.Length > 1:
                        dist = min(calc_dist(other.Head, snake.Head),
                                   calc_dist(other.Head, snake.Segments[0]))
                        if dist < best_dist:
                            best_dist = dist
                            best_snake = snake
                if best_snake:
                    best_snake.Hunt = other
                    other.Hunt = True
                    print("The HUNT is ON! {} -> {} @ {}".format(best_snake.Name, other.Name, other.Length))

        # start defensive hunts
        for snake in self.Snakes:
            for other in self.OtherSnakes:
                if other.Length == 1:  # assume only size 1 snakes are aggressive
                    if (calc_dist(snake.Head, other.Head) == 1) or (calc_dist(snake.Segments[0], other.Head) == 1):
                        snake.Hunt = other
                        other.Hunt = True
                        print("Defensive HUNT! {} -> {}".format(snake.Name, other.Name, other.Length))

        # perform actual splits (hunts and food collection)
        for snake in self.Snakes:
            cut_point = None
            # ensure hunter is size 1
            if snake.Hunt and snake.Length > 1:
                dist_head = calc_dist(snake.Hunt.Head, snake.Head)
                dist_tail = calc_dist(snake.Hunt.Head, snake.Segments[0])
                if dist_head < dist_tail:
                    cut_point = snake.Length - 1
                    new_snake = self.split_snake(snake, cut_point)
                    new_snake.Hunt = None
                else:
                    cut_point = 1
                    new_snake = self.split_snake(snake, cut_point)
                    new_snake.Hunt = snake.Hunt
                    snake.Hunt = None
                print("Split off HUNTER {} {}".format(snake.Name, new_snake.Name))

            # split snakes to parallelize food collecting
            if snake.Length >= 4 and len(self.Snakes) < len(self.Foods) / 15:
                cut_point = 2
                new_snake = self.split_snake(snake, cut_point)
            if cut_point:
                splits.append(player_pb2.SplitRequest(playerIdentifier=playerIdentifier, newSnakeName=new_snake.Name,
                                                      oldSnakeName=snake.Name, snakeSegment=cut_point,
                                                      nextLocation=new_snake.Head))
        return splits



async def ListenToServerEvents() -> None:
        with grpc.insecure_channel("192.168.178.62:5168") as channel:
            stub = player_pb2_grpc.PlayerHostStub(channel)
            for thing in stub.SubscribeToServerEvents(player_pb2.EmptyRequest()):
                print(thing)

def Register(playerName):
    with grpc.insecure_channel("192.168.178.62:5168") as channel:
        stub = player_pb2_grpc.PlayerHostStub(channel)
        registerResponse = stub.Register(player_pb2.RegisterRequest(playerName=playerName))
        global playerIdentifier
        gameState = GameState(registerResponse.dimensions, registerResponse.startAddress, playerName)
        playerIdentifier = registerResponse.playerIdentifier
        initial_state = stub.GetGameState(player_pb2.EmptyRequest())
        gameState.set_state(initial_state)
        return gameState

async def Subscribe(gameState) -> None:
        with grpc.insecure_channel("192.168.178.62:5168") as channel:
            stub = player_pb2_grpc.PlayerHostStub(channel)
            for thing in stub.Subscribe(player_pb2.SubsribeRequest(playerIdentifier=playerIdentifier)):
                gameState.update(gameUpdate=thing)
                for split in gameState.getSplits():
                    stub.SplitSnake(split)
                for move in gameState.getMoves():
                    #print(move.snakeName + ": " + str(move.nextLocation))
                    stub.MakeMove(move)

async def main():
    #asyncio.create_task(ListenToServerEvents())
    gameState = Register(MY_NAME)
    asyncio.create_task(Subscribe(gameState))



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())