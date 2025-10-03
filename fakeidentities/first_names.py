from collections import defaultdict
from dataclasses import dataclass

from fuzzy import nysiis

from fakeidentities.data import ALL_BABY_NAMES
from nicknames import default_lookup

from rapidfuzz import process
from fakeidentities.match import PhoneticMatch, PureMatch, Match, NickNameMatch


@dataclass
class FirstNames:

    def __init__(self):
        self._nickname_reverse_lookup = defaultdict(set)
        self._all_first_names = list({ self._normalize(name) for name in ALL_BABY_NAMES['name'].to_list() })
        self._phonetic_map = defaultdict(list)
        for name in self._all_first_names:
            self._phonetic_map[nysiis(name)].append(name)
        nicknames_lookup = default_lookup()
        for canonical, associated_nicknames in nicknames_lookup.items():
            for nickname in associated_nicknames:
                self._nickname_reverse_lookup[nickname].add(self._normalize(canonical))
        # Build an ANN index using embeddings
        # self._model = SentenceTransformer('all-MiniLM-L6-v2')
        # embeddings = self._model.encode(self._all_first_names)
        # self._first_names_embeddings = np.array(embeddings).astype("float32")
        # dimension = self._first_names_embeddings.shape[1]
        # self._index = faiss.IndexFlatL2(dimension)
        # self._index.add(self._first_names_embeddings)



    def first_name_matches(self, normalized_candidate: str) -> PureMatch | None:
        return PureMatch(normalized_candidate) if normalized_candidate in self._all_first_names else None

    def nickname_matches(self, normalized_candidate: str) -> NickNameMatch | None:
        matches = self._nickname_reverse_lookup.get(normalized_candidate)
        if matches:
            return NickNameMatch(self._closest_match(normalized_candidate, list(matches)))
        return None

    def phonetic_matches(self, candidate: str) -> PhoneticMatch | None:
        try:
            sound = nysiis(candidate)
            matches = self._phonetic_map.get(sound)
            if matches:
                return PhoneticMatch(self._closest_match(candidate, matches))
        except Exception as e:
            print(f"could not soundex: {candidate}: ", e)
        return None

    def matches(self, candidate: str) -> Match | None:
        if not candidate:
            return None
        normalized = self._normalize(candidate)
        fn_match = self.first_name_matches(normalized)
        if fn_match:
            return fn_match

        nickname_match = self.nickname_matches(normalized)
        if nickname_match:
            return nickname_match

        return self.phonetic_matches(normalized)


    def _closest_match(self, normalized: str, candidates: list[str]) -> str:
        scores = process.cdist([normalized], candidates)
        return candidates[scores.argmax(axis=1)[0]]

    def nearest_neighbour(self, candidate: str) -> str | None:
        query_embedding = self._model._metaphone_encode([self._normalize(candidate)]).astype("float32")
        distances, indices = self._index.search(query_embedding, 1)
        nearest_neighbour, distance = [(self._all_first_names[idx], distances[0][i]) for i, idx in enumerate(indices[0])][0]
        return nearest_neighbour if distance < 0.15 else None

    @staticmethod
    def _normalize(inp: str) -> str:
        return inp.lower().strip()
