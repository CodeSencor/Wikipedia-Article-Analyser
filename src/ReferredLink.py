class ReferredLink:
    def __init__(self, link, referral):
        self.link = link
        self.referral = referral

    def __hash__(self):
        return hash(self.link)

    def __eq__(self, other):
        if isinstance(other, ReferredLink):
            return self.link == other.link
        return False

    def __repr__(self):
        return f"ReferredLink({self.link!r}, {self.referral!r})"
