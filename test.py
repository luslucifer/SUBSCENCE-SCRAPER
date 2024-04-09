from thefuzz import fuzz

string1 = 'Eye Love You (Ai Rabu Yuu / アイラブユー) - First Season'
tmdb ='Eye Love You'

similarity_ratio = fuzz.ratio(tmdb, string1)
print(similarity_ratio)
                # Using fuzz.partial_ratio
partial_ratio = fuzz.partial_ratio(tmdb, string1)
print(partial_ratio)                # Using fuzz.token_sort_ratio
token_sort_ratio = fuzz.token_sort_ratio(tmdb, string1)
print(token_sort_ratio)                # Using fuzz.token_set_ratio
token_set_ratio = fuzz.token_set_ratio(tmdb, string1)
print(token_set_ratio)