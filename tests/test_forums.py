
class TestForums:

    def test_with_none_name_in_dcard_instance(self, dcard):
        f = dcard.forums
        assert f.name is None

    def test_with_name_param_through__call__(self, dcard):
        name = 'testclass'
        f = dcard.forums(name)
        assert name == f.name
        assert name in f.posts_meta_url

    def test_get_all_forums(self, dcard):
        all_fourums = dcard.forums.get()
        assert all_fourums

    def test_get_only_normal_forums(self, dcard):
        no_school_fourums = dcard.forums.get(no_school=True)
        assert no_school_fourums

    def test_extract_general_forums(self, dcard):
        all_fourums = dcard.forums.get()
        no_school_fourums = dcard.forums.get(no_school=True)
        assert len(all_fourums) > len(no_school_fourums)

        extracted = dcard.forums._extract_general(all_fourums)
        assert len(no_school_fourums) == len(list(extracted))

    def test_get_metas_with_sort_param(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)
        assert len(forum.get_metas(sort='popular')) == 30
        assert len(forum.get_metas(sort='new')) == 30

    def test_get_metas_with_num_param(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)
        assert len(forum.get_metas()) == 30
        assert len(forum.get_metas(num=0)) == 0
        assert len(forum.get_metas(num=90)) == 90
        assert len(forum.get_metas(num=33)) == 33
        assert len(forum.get_metas(num=87)) == 87
        assert len(forum.get_metas(num=999)) == 999

    def test_get_metas_with_time_bound_param(self, dcard, boundary_date):
        name = 'testclass'
        forum = dcard.forums(name)
        assert len(forum.get_metas()) == 30
        assert len(forum.get_metas(timebound='')) == 30
        assert len(forum.get_metas(timebound=boundary_date.isoformat())) == 0

    def test_get_metas_with_infinite_pages(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)
        assert len(forum.get_metas(num=forum.infinite_page)) >= 30

    def test_get_metas_with_callback_collect_ids(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)

        def collect_ids(metas):
            return [meta['id'] for meta in metas]

        ids = forum(name).get_metas(callback=collect_ids)
        assert len(ids) == 30
        assert all([isinstance(x, int) for x in ids])

    def test_get_metas_with_callback_no_return(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)

        def with_no_return(metas):
            return None

        no_return = forum(name).get_metas(callback=with_no_return)
        assert no_return is None

    def test_get_metas_with_callback_store_db(self, dcard):
        name = 'testclass'
        forum = dcard.forums(name)

        def simulate_store_into_db(metas):
            some_ids = [9487] * len(metas)
            return some_ids

        result_ids = forum.get_metas(callback=simulate_store_into_db)
        assert len(result_ids) == 30
