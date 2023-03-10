import git

repo = git.Repo()


def get_remote_url() -> str:
    return repo.remotes.origin.url


def get_local_commit() -> str:
    return str(repo.commit())


def pull_from_remote() -> git.FetchInfo:
    return repo.remotes.origin.pull()


def get_updates_info() -> tuple[str, str] | None:
    if result := repo.remotes.origin.fetch(verbose=False):
        return str(commit := result[0].commit), commit.summary


def merge_up_to(commit_id: str) -> str:
    return repo.git.merge(commit_id)
