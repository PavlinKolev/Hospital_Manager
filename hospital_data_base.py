import sqlite3
from prettytable import PrettyTable
from queries import *
from settings import DEFAULT_HOSPITAL_NAME, ACADEMIC_TITLES, INJURIES
from validations import(validate_username, validate_password, validate_age,
                        validate_injury, validate_academic_title)
from password import encode
from helper_prints import print_choose_academic_title
from doctor import Doctor
from patient import Patient


class HospitalDB:
    def __init__(self, name=DEFAULT_HOSPITAL_NAME):
        self.db = sqlite3.connect(name + '.db')
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.__create_user_table()
        self.__create_doctors_table()
        self.__create_patients_table()
        self.__create_hospital_stay_table()
        self.__create_visitation_table()
        self.set_users_ids()
        self.set_patients_ids()
        self.set_doctors_ids()
        self.set_hospital_ids()
        self.set_visitations_ids()

    def __del__(self):
        self.__close_data_base()

    # we want to close the database even if not handled exeption occurs
    def __exit__(Self, exc_type, exc_value, traceback):
        self.__close_data_base()

    def set_users_ids(self):
        self.cursor.execute(LIST_USER_IDS)
        users = self.cursor.fetchall()
        self.users_ids = [u["ID"] for u in users]

    def set_patients_ids(self):
        self.cursor.execute(LIST_PATIENT_IDS)
        patients = self.cursor.fetchall()
        self.patients_ids = [p["ID"] for p in patients]

    def set_doctors_ids(self):
        self.cursor.execute(LIST_DOCTOR_IDS)
        doctors = self.cursor.fetchall()
        self.doctors_ids = [d["ID"] for d in doctors]

    def set_hospital_ids(self):
        self.cursor.execute(LIST_HOSPITAL_STAY_IDS)
        hospital_stays = self.cursor.fetchall()
        self.hospital_stay_ids = [hs["ID"] for hs in hospital_stays]

    def set_visitations_ids(self):
        self.cursor.execute(LIST_VISITATION_IDS)
        visitations = self.cursor.fetchall()
        self.visitations_ids = [v["ID"] for v in visitations]

    def __create_user_table(self):
        self.cursor.execute(CREATE_USER_TABLE)
        self.db.commit()

    def __create_patients_table(self):
        self.cursor.execute(CREATE_PATIENT_TABLE)
        self.db.commit()

    def __create_doctors_table(self):
        self.cursor.execute(CREATE_DOCTOR_TABLE)
        self.db.commit()

    def __create_hospital_stay_table(self):
        self.cursor.execute(CREATE_HOSPITAL_STAY_TABLE)
        self.db.commit()

    def __create_visitation_table(self):
        self.cursor.execute(CREATE_VISITATION_TABLE)
        self.db.commit()

    def __add_user(self, username, password, age):
        validate_username(username)
        validate_password(password)
        validate_age(age)
        self.cursor.execute(ADD_USER, (username, encode(password), age))
        self.users_ids.append(self.cursor.lastrowid)

    def add_patient(self, username, password, age, doctor_id):
        self.__add_user(username, password, age)
        self.__validate_doctor_id(doctor_id)
        user_id = self.users_ids[-1]
        self.cursor.execute(ADD_PATIENT, (user_id, doctor_id))
        self.db.commit()
        self.patients_ids.append(user_id)

    def add_doctor(self, username, password, age, academic_title):
        self.__add_user(username, password, age)
        validate_academic_title(academic_title)
        user_id = self.users_ids[-1]
        self.cursor.execute(ADD_DOCTOR, (user_id, academic_title))
        self.db.commit()
        self.doctors_ids.append(user_id)

    def add_hospital_stay(self, startdate, room, patient_id, injury, enddate=None):
        validate_injury(injury)
        self.__validate_patient_id(patient_id)
        self.cursor.execute(ADD_HOSPITAL_STAY,
                            (startdate, enddate, room, injury, patient_id))
        self.db.commit()
        self.hospital_stay_ids.append(self.cursor.lastrowid)

    def add_visitation(self, doctor_id, start_hour, patient_id=None):
        self.__validate_doctor_id(doctor_id)
        if patient_id:
            self.__validate_patient_id(patient_id)
        self.cursor.execute(ADD_VISITATION, (patient_id, doctor_id, start_hour))
        self.db.commit()
        self.visitations_ids.append(self.cursor.lastrowid)

    def delete_free_visitations_of_doctor(self, doctor_id):
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(DELETE_FREE_VISITATIONS_OF_DOCTOR, (doctor_id, ))
        self.db.commit()

    def get_accademic_title_of_doctor(self, doctor_id):
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(DOCTOR_ACCADEMIC_TITLE, (doctor_id, ))
        return self.cursor.fetchone()["ACCADEMIC_TITLE"]

    def list_all_doctors(self):
        self.cursor.execute(LIST_ALL_DOCTORS)
        doctors = self.cursor.fetchall()
        table = PrettyTable()
        table.field_names = ["Id", "Username", "Academic title"]
        for d in doctors:
            table.add_row(d)
        print(table)

    def list_free_visitations_of_doctor(self, doctor_id):
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(LIST_FREE_VISITATIONS_OF_DOCTOR, (doctor_id, ))
        visitations = self.cursor.fetchall()
        table = PrettyTable()
        table.field_names = ["Id", "Start hour"]
        for v in visitations:
            table.add_row(v)
        print(table)

    def list_room_and_hs_durations_of_patients(self, doctor_id):
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(ROOM_AND_HS_DURATION_OF_DOCTOR_PATIENTS,(doctor_id, ))
        patients_hs = self.cursor.fetchall()
        table = PrettyTable()
        table.field_names = ["Username", "Room", "Startdate", "Enddate"]
        for p in patients_hs:
            table.add_row(p)
        print(table)

    def list_hs_of_patient(self, patient_id):
        self.__validate_patient_id(patient_id)
        self.cursor.execute(LIST_HS_FOR_PATIENT, (patient_id, ))
        hospital_stays = self.cursor.fetchall()
        table = PrettyTable()
        table.field_names = ["Startdate", "Enddate", "Room", "Injury"]
        for hs in hospital_stays:
            table.add_row(hs)
        print(table)

    def update_user_username(self, user_id, username):
        validate_username(username)
        self.__validate_user_id(user_id)
        self.cursor.execute(UPDATE_USER_USERNAME, (username, user_id))
        self.db.commit()

    def update_user_age(self, user_id, age):
        validate_age(age)
        self.__validate_user_id(user_id)
        self.cursor.execute(UPDATE_USER_AGE, (age, user_id))
        self.db.commit()

    def update_patient_doctors_id(self, patient_id, doctor_id):
        self.__validate_patient_id(patient_id)
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(UPDATE_PATIENT_DOCTOR_ID, (doctor_id, patient_id))
        self.db.commit()

    def update_visitation_patient_id(self, visitation_id, patient_id):
        self.__validate_visitation_id(visitation_id)
        self.__validate_patient_id(patient_id)
        self.cursor.execute(UPDATE_VISITATION_PATIENT_ID, (patient_id, visitation_id))
        self.db.commit()

    def all_patients_by_doctor(self, doctor_id):
        self.__validate_doctor_id(doctor_id)
        self.cursor.execute(LIST_PATIENTS_OF_DOCTOR, (doctor_id,))
        self.__print_patients_after_query()

    def register_user(self, username, password, age):
        user = self.promote_user(username, password, age)
        self.__make_user_active(user.get_id())
        user.run_interface(self)

    def promote_user(self, username, password, age):
        if HospitalDB.is_doctor_username(username):
            return self.promote_to_doctor(username, password, age)
        return self.promote_to_patient(username, password, age)

    def promote_to_doctor(self, username, password, age):
        print_choose_academic_title()
        accademic_title = input("accademic title:> ")
        self.add_doctor(username, password, age, accademic_title)
        doctor_id = self.doctors_ids[-1]
        return Doctor(username, age, doctor_id, accademic_title)

    def promote_to_patient(self, username, password, age):
        print("Choose which doctor...")
        self.list_all_doctors()
        doctor_id = int(input("Doctor ID:> "))
        self.add_patient(username, password, age, doctor_id)
        patient_id = self.patients_ids[-1]
        return Patient(username, age, patient_id, doctor_id)

    def login_user(self, username, password):
        user_id = self.__get_id_of_username(username)
        self.__validate_password_of_user(user_id, password)
        user = self.__get_user_as_object(user_id, username)
        self.__make_user_active(user_id)
        user.run_interface(self)

    def __get_id_of_username(self, username):
        self.cursor.execute(ID_OF_USER_BY_USERNAME, (username, ))
        result = self.cursor.fetchone()
        if result is None:
            raise ValueError("No user wtih this username.")
        return result["ID"]

    def __validate_password_of_user(self, user_id, password):
        self.cursor.execute(PASSWORD_OF_USER, (user_id, ))
        user_password = self.cursor.fetchone()["PASSWORD"]
        if encode(password) != user_password:
            raise ValueError("Wrong password for this username.")

    def logout_user(self, user_id):
        self.__validate_user_id(user_id)
        self.cursor.execute(UPDATE_USER_IS_ACTIVE, (0, user_id))
        self.db.commit()

    def __get_user_as_object(self, user_id, user_name):
        if HospitalDB.is_doctor_username(user_name):
            return self.__get_doctor_object(user_id)
        return self.__get_patient_object(user_id)

    def __get_doctor_object(self, user_id):
        self.__validate_doctor_id(user_id)
        self.cursor.execute(DOCTOR_DATA, (user_id, ))
        data = self.cursor.fetchone()
        return Doctor(data[0], data[1], data[2], data[3])

    def __get_patient_object(self, user_id):
        self.__validate_patient_id(user_id)
        self.cursor.execute(PATIENT_DATA, (user_id, ))
        data = self.cursor.fetchone()
        return Patient(data[0], data[1], data[2], data[3])

    def __make_user_active(self, user_id):
        if self.__is_user_logged_in(user_id):
            raise ValueError("This user is already logged in" +
                            "from another application.")
        self.cursor.execute(UPDATE_USER_IS_ACTIVE, (1, user_id))
        self.db.commit()

    def __is_user_logged_in(self, user_id):
        self.__validate_user_id(user_id)
        self.cursor.execute(USER_STATUS, (user_id, ))
        return (self.cursor.fetchone()["IS_ACTIVE"] != 0)

    def __close_data_base(self):
        self.cursor.execute(MAKE_ALL_USERS_NOT_LOGGED)
        self.db.commit()
        self.db.close()

    def __print_patients_after_query(self):
        patients = self.cursor.fetchall()
        table = PrettyTable()
        table.field_names = ["ID", "Username", "Age"]
        for p in patients:
            table.add_row(p)
        print(table)

    def __validate_user_id(self, user_id):
        if user_id not in self.users_ids:
            raise ValueError("There is no user with this id.")

    def __validate_patient_id(self, patient_id):
        if patient_id not in self.patients_ids:
            raise ValueError("There is no patient with this ID.")

    def __validate_doctor_id(self, doctor_id):
        if doctor_id not in self.doctors_ids:
            raise ValueError("There is no doctor with this id.")

    def __validate_hs_id(self, hs_id):
        if hs_id not in self.hospital_stay_ids:
            raise ValueError("There is no hospidatl stay with this id.")

    def __validate_visitation_id(self, visitation_id):
        if visitation_id not in self.visitations_ids:
            raise ValueError("There is no visitation with this id.")

    @staticmethod
    def is_doctor_username(username):
        return username.startswith("Dr.")
