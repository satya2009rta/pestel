class Antichain(object):
    """
    An antichain is a collection of incomparable elements.
    """

    def __init__(self, comparator, intersector):
        """
        An antichain is a collection of incomparable elements. These elements
        are stored in an internal list.  The size of the antichain is also
        recorded internally. Two functions allow for comparison between and
        intersection of elements.
        :param comparator:
        :type comparator:
        :param intersector:
        :type intersector:
        """
        self.incomparable_elements = []
        self.size = 0
        self.comparator = comparator
        self.intersector = intersector

    def insert(self, element):
        """
        If element is incomparable to any element contained in the antichain,
        element is added to the antichain.  If there exists x in the antichain
        such that x > element (according to comparator), do nothing.
        Otherwise, all x in the antichain such that element > x are removed
        from the antichain.  This method modifies the antichain.
        :param element:
        :type element:
        :return:
        :rtype:
        """
        resulting_incomparable_elements = []
        resulting_size = 0

        for s in self.incomparable_elements:

            # Element is smaller than some element of the antichain
            if self.comparator(element, s):
                return self

            # If element is not smaller than s, it is either incomparable to or
            # bigger than s
            # If incomparable, we add s. If bigger we don't. We therefore check
            # if s < element.
            # If element is not bigger than s or is incomparable, add s to
            # result
            if not (self.comparator(s, element)):
                resulting_incomparable_elements.append(s)
                resulting_size += 1

        # Add the new element
        resulting_incomparable_elements.append(element)
        resulting_size += 1

        self.incomparable_elements = resulting_incomparable_elements

        return None

    def union(self, antichain):
        """
        Computes the union of two antichains. The resulting antichain is
        returned.  This modifies the first antichain.
        :param antichain:
        :type antichain:
        :return:
        :rtype:
        """
        for s in antichain.incomparable_elements:
            self.insert(s)
        return self

    def intersection(self, antichain):
        """
        Computes the greatest lower bound of antichain1 and antichain2.
        This returns a new antichain.
        :param antichain:
        :return:
        """
        resulting_antichain = Antichain(self.comparator, self.intersector)

        for set1 in self.incomparable_elements:
            for set2 in antichain.incomparable_elements:
                temp = self.intersector(set1, set2)
                # intersector yields -1 when intersection does not exist
                if temp != -1:
                    resulting_antichain.insert(temp)

        return resulting_antichain

    def contains(self, element):
        """
        Check whether the antichain contains the element exactly.
        :param element:
        :return:
        """

        # TODO should this not check actual inclusion w.r.t.
        # the order on elements ?

        for i in self.incomparable_elements:
            if i == element:
                return True
        return False

    def contains_element(self, element):
        """
        Check whether the antichain contains the element in its closure i.e. element is smaller than some element
        in the antichain.
        :param element:
        :return:
        """

        for i in self.incomparable_elements:
            if self.comparator(element,i):
                return True
        return False

    def compare(self, antichain):
        """
        Compare two antichains to check if they are identical.
        :param antichain:
        :type antichain:
        :return:
        :rtype:
        """
        for element in self.incomparable_elements:
            if not antichain.contains(element):
                return False
        """ TODO
        for element in antichain.incomparable_elements:
            if not self.contains(element):
                return False
        """

        return True

    def __repr__(self):
        res = "{ "
        for element in self.incomparable_elements:
            res += str(element) + ", "
        res = res[:-1]
        res += "}"
        return res

        """
        res = "{"
        for element in self.incomparable_elements:
            res += "[" + str(element[0]) + " ,"
            for function in element[1:]:
                res += "("
                for count in function:
                    if count != 3:
                        res += str(count) + ", "
                    else:
                        res += '-, '
                res = res[:-2]
                res += "), "
            res = res[:-2]

            res += "] ,"
        res += "}"
        return res """
