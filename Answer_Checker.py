from gingerit.gingerit import GingerIt
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

def check_answer(given_answer, correct_answer):
    given_answer_length=len(given_answer.split())
    if given_answer_length == 0:
        final_score = 0
    else:
        l = given_answer_length/len(correct_answer.split())
        # l=1
        if l > 1:
            l = 1

        #     to correct grammatical errors
        parser = GingerIt()
        response = parser.parse(given_answer)

        model = SentenceTransformer('all-mpnet-base-v2')
        # Embedding the texts into vectors using SBERT
        given_answer_vector = model.encode(response['result'], convert_to_tensor=True)
        correct_answer_vector = model.encode(correct_answer, convert_to_tensor=True)

        # Calculating the cosine similarity between the vectors
        c = 1 - cosine(given_answer_vector, correct_answer_vector)

        #EVALUATE
        # final_score = ((85*c + 15*g)/100)*l*100
        # final_score = c*100
        final_score = c * l * 100
        if final_score < 0:
            final_score = 0
    print(final_score)
    return final_score
