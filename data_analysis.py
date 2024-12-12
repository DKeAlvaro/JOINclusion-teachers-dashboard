def filter_non_played(data):    
    filtered_students = 0
    filtered_data = []
    for student in data:
        ethnicity = student["survey"]["Ethnicity"]
        if ethnicity == "" or ethnicity == "0":
            student["survey"]["Ethnicity"] = "Ethnicity Not specified"
        tot_score = 0
        for session in student["data"]:
            tot_score += session["scores"]["total_score"]
        if tot_score != 0:
            filtered_data.append(student)
        else:
            filtered_students += 1
    if filtered_students != 0:
        print(f"Filtered students: {filtered_students} out of {len(data)}. (Score of 0)")
    return filtered_data

def get_different_types(students_data):
    unique_backgrounds = []
    unique_languages = []
    unique_ethnicities = []
    for student in students_data:
        background = student["survey"]["MigrantBackground"]
        if background not in unique_backgrounds:
            unique_backgrounds.append(background)
        language = student["survey"]["Language"]
        if language not in unique_languages:
            unique_languages.append(language)

        ethnicity = student["survey"]["Ethnicity"]
        if ethnicity not in unique_ethnicities:
            unique_ethnicities.append(ethnicity)

    return unique_backgrounds, unique_languages, unique_ethnicities

def one_hot_encode(value, unique_values):
    one_hot_vector = [0] * len(unique_values)
    index = unique_values.index(value)
    one_hot_vector[index] = 1
    return one_hot_vector

def get_student_vector(student, unique_backgrounds, unique_languages, unique_ethnicities):

    background = student["survey"]["MigrantBackground"]
    language = student["survey"]["Language"]
    ethnicity = student["survey"]["Ethnicity"]
    age                = int(student["survey"]["Age"]) 
    migration_age      = int(student["survey"]["MigrationAge"]) if student["survey"]["MigrationAge"] != "" else -1
    adoption           = 1 if student["survey"]["Adopted"] == 'Yes' else 0
    gender_sex         = 1 if student["survey"]["Sex"] == 'Boy' else 0

    total_time_played = 0
    total_interactions = 0
    total_helps = 0

    total_help_s1 = 0
    total_help_s2 = 0

    best_score_s1 = 0
    best_score_s2 = 0

    total_character_interactions_s1 = 0
    total_character_interactions_s2 = 0
    total_change_scene_interactions_s1 = 0
    total_change_scene_interactions_s2 = 0
    total_movement_interactions_s1 = 0
    total_movement_interactions_s2 = 0

    num_sessions = 0

    name = student["student"]
    
    for session in student["data"]:
        if session["scores"]["total_score"] != 0:
            total_time_played += session["duration"]
            total_interactions += session["interaction"]["total_interactions"]
            total_helps += session["helps"]["total_help"]
            score_s1 = session["scores"]["breakdown"][0]["total_score"]#/session["scores"]["breakdown"][0]["max_score"] if session["scores"]["breakdown"][0]["max_score"] != 0 else 0
            score_s2 = session["scores"]["breakdown"][1]["total_score"]#/session["scores"]["breakdown"][1]["max_score"] if session["scores"]["breakdown"][1]["max_score"] != 0 else 0
            best_score_s1 = max(best_score_s1, score_s1)
            best_score_s2 = max(best_score_s2, score_s2)

            total_help_s1 += session["helps"]["breakdown"][0]["total"]
            total_help_s2 += session["helps"]["breakdown"][1]["total"]

            total_character_interactions_s1 += session["interaction"]["character"]["breakdown"][0]["total"]
            total_character_interactions_s2 += session["interaction"]["character"]["breakdown"][1]["total"]
            total_change_scene_interactions_s1 += session["interaction"]["change_scene"]["breakdown"][0]["total"]
            total_change_scene_interactions_s2 += session["interaction"]["change_scene"]["breakdown"][1]["total"]
            total_movement_interactions_s1 += session["interaction"]["movement"]["breakdown"][0]["total"]
            total_movement_interactions_s2 += session["interaction"]["movement"]["breakdown"][1]["total"]

            num_sessions += 1

    best_score = best_score_s1 + best_score_s2

    interaction_vector = [name, best_score, num_sessions, total_time_played, total_interactions, total_helps]
    interaction_vector.extend([best_score_s1, best_score_s2, total_help_s1, total_help_s2])
    interaction_vector.extend([total_character_interactions_s1, total_character_interactions_s2])
    interaction_vector.extend([total_change_scene_interactions_s1, total_change_scene_interactions_s2])
    interaction_vector.extend([total_movement_interactions_s1, total_movement_interactions_s2])

    full_vector = interaction_vector.copy()
    full_vector.extend([age, migration_age, adoption, gender_sex])
    
    background_vector = one_hot_encode(background, unique_backgrounds)
    language_vector = one_hot_encode(language, unique_languages)
    ethnicity_vector = one_hot_encode(ethnicity, unique_ethnicities)
    demographic_vector = background_vector + language_vector + ethnicity_vector
    
    full_vector.extend(demographic_vector)
    return interaction_vector, full_vector


def get_feature_vectors(students_data):
    unique_backgrounds, unique_languages, unique_ethnicities = get_different_types(students_data)
    features = ["name", "best_score","num_sessions", "total_time_played", "total_interactions", "total_helps"]
    features.extend(["best_score_s1", "best_score_s2", "total_help_s1", "total_help_s2"])
    features.extend(["total_character_interactions_s1", "total_character_interactions_s2"])
    features.extend(["total_change_scene_interactions_s1", "total_change_scene_interactions_s2"])
    features.extend(["total_movement_interactions_s1", "total_movement_interactions_s2"])
    features.extend(["age", "migration_age", "adoption", "gender_sex"])
    features.extend(unique_backgrounds)
    features.extend(unique_languages)
    features.extend(unique_ethnicities)

    interaction_vectors = []
    full_vectors = []
    usernames = []
    index = 0
    for student in students_data:
        intr_vector, full_vector = get_student_vector(student, unique_backgrounds, unique_languages, unique_ethnicities)
        interaction_vectors.append(intr_vector)
        full_vectors.append(full_vector)
        usernames.append(student["student"])
        index += 1

    return interaction_vectors, full_vectors, usernames, features
