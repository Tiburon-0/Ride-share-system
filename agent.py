from ride import Ride


class Agent:

    '''Automated system agent that selects drivers, creates rides, and logs events'''

    def __init__(self, agent_id):
        self.__agent_id = agent_id
        self.__logs = []

    # Getter methods
    def get_agent_id(self):
        '''Returns agent_id'''
        return f"Assigned agent: {self.__agent_id}"

    def get_logs(self):
        '''Returns logs'''
        return self.__logs

    # Service methods

    def select_driver(self, drivers):
        if len(drivers) > 0:
            selected_driver = drivers[0]
            print(f"{self.__agent_id} has selected Driver: {selected_driver}")
            return selected_driver
        else:
            return f"No drivers available. Please standby."

    def create_a_ride(self, rider, driver, destination):
        '''Creates a ride using rider-driver match and destination'''
        ride = Ride(rider, driver, destination)
        rider_name = rider.get_name()
        driver_name = driver.get_name()
        print(
            f"Ride created: {driver_name} is picking up {rider_name} to travel to {destination}.")
        self.__logs.append(ride)
        return ride

    def override_decision(self, ride, updated_driver):
        previous_driver = ride.get_driver()
        updated_driver = ride.set_driver(updated_driver)
        print(
            f"Driver changed from {previous_driver.get_name()} to {updated_driver.get_name()}.")
        log_entry = f"[Agent Override]: Driver changed from {previous_driver.get_name()} to {updated_driver.get_name()}."
        self.__logs.append(log_entry)
        return updated_driver

    def log_ride(self, ride, event_description):
        '''Logs ride data'''
        log_entry = f"[{event_description}], {ride}"
        self.__logs.append(log_entry)
        return self.__logs

    def show_logs(self):
        '''Displays system logs'''
        print(f"-----SYSTEM AGENT LOGS-----")
        print(f"Referencing logs for: {self.__agent_id}")

        if len(self.__logs) > 0:
            for log in self.__logs:
                print(log)
        else:
            print("No events logged yet.")
        return self.__logs
