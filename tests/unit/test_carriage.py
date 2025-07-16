# import pytest

# # Import your Carriage and Passenger classes:
# from core.trains.carriage import Carriage
# from core.passenger import Passenger

# dummy_passenger = Passenger()

# def make_passengers(n):
#     """Helper to create a list of dummy passengers."""
#     return [DummyPassenger(f"P{i}") for i in range(n)]

# def test_empty_carriage():
#     c = Carriage(max_capacity=3)
#     assert c.max_capacity == 3
#     assert len(c.passengers) == 0
#     assert c.available_capacity() == 3
#     assert not c.is_full()

# def test_load_fits_within_capacity():
#     c = Carriage(max_capacity=3)
#     p_list = make_passengers(2)
#     overflow = c.load(p_list)
#     assert len(c.passengers) == 2
#     assert overflow == []
#     assert c.available_capacity() == 1

# def test_load_exact_capacity():
#     c = Carriage(max_capacity=2)
#     p_list = make_passengers(2)
#     overflow = c.load(p_list)
#     assert len(c.passengers) == 2
#     assert overflow == []
#     assert c.is_full()

# def test_load_over_capacity():
#     c = Carriage(max_capacity=2)
#     p_list = make_passengers(5)
#     overflow = c.load(p_list)
#     assert len(c.passengers) == 2
#     assert overflow == p_list[2:]

# def test_load_in_multiple_batches():
#     c = Carriage(max_capacity=3)
#     batch1 = make_passengers(2)
#     batch2 = make_passengers(3)
#     overflow1 = c.load(batch1)
#     assert overflow1 == []
#     assert len(c.passengers) == 2
#     overflow2 = c.load(batch2)
#     assert len(c.passengers) == 3
#     assert overflow2 == batch2[1:]  # Only one from batch2 could board

# def test_unload_by_number():
#     c = Carriage(max_capacity=4)
#     p_list = make_passengers(4)
#     c.load(p_list)
#     removed = c.unload(number=2)
#     assert len(removed) == 2
#     assert len(c.passengers) == 2

# def test_unload_with_criteria():
#     c = Carriage(max_capacity=4)
#     p_list = make_passengers(4)
#     c.load(p_list)
#     # Remove only passengers whose name ends with "1"
#     removed = c.unload(criteria=lambda p: p.name.endswith("1"))
#     assert len(removed) == 1
#     assert all(p.name != "P1" for p in c.passengers)

# def test_empty():
#     c = Carriage(max_capacity=3)
#     c.load(make_passengers(3))
#     c.empty()
#     assert len(c.passengers) == 0
#     assert not c.is_full()

# def test_repr():
#     c = Carriage(max_capacity=2)
#     assert "Carriage" in repr(c)