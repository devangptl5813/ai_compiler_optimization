/* Inlined header patricia.h */
/*
 * patricia.h
 *
 * Patricia trie implementation.
 *
 * Functions for inserting nodes, removing nodes, and searching in
 * a Patricia trie designed for IP addresses and netmasks.  A
 * head node must be created with (key,mask) = (0,0).
 *
 * NOTE: The fact that we keep multiple masks per node makes this
 *       more complicated/computationally expensive then a standard
 *       trie.  This is because we need to do longest prefix matching,
 *       which is useful for computer networks, but not as useful
 *       elsewhere.
 *
 * Matthew Smart <mcsmart@eecs.umich.edu>
 *
 * Copyright (c) 2000
 * The Regents of the University of Michigan
 * All rights reserved
 *
 * $Id: patricia.h,v 1.1.1.1 2000/11/06 19:53:17 mguthaus Exp $
 */

#ifndef _PATRICIA_H_
#define _PATRICIA_H_


/*
 * Patricia tree mask.
 * Each node in the tree can contain multiple masks, so this
 * structure is where the mask and data are kept.
 */
struct ptree_mask {
	unsigned long pm_mask;
	void *pm_data;
};


/*
 * Patricia tree node.
 */
struct ptree {
	unsigned long p_key;		/* Node key		*/
	struct ptree_mask *p_m;		/* Node masks		*/
	unsigned char p_mlen;		/* Number of masks	*/
	char p_b;			/* Bit to check		*/
	struct ptree *p_left;		/* Left pointer		*/
	struct ptree *p_right;		/* Right pointer	*/
};


extern struct ptree *pat_insert(struct ptree *n, struct ptree *head);
extern int           pat_remove(struct ptree *n, struct ptree *head);
extern struct ptree *pat_search(unsigned long key, struct ptree *head);

#endif /* _PATRICIA_H_ */

/* Inlined source patricia.c */
/*
 * patricia.c
 *
 * Patricia trie implementation.
 *
 * Functions for inserting nodes, removing nodes, and searching in
 * a Patricia trie designed for IP addresses and netmasks.  A
 * head node must be created with (key,mask) = (0,0).
 *
 * NOTE: The fact that we keep multiple masks per node makes this
 *       more complicated/computationally expensive then a standard
 *       trie.  This is because we need to do longest prefix matching,
 *       which is useful for computer networks, but not as useful
 *       elsewhere.
 *
 * Matthew Smart <mcsmart@eecs.umich.edu>
 *
 * Copyright (c) 2000
 * The Regents of the University of Michigan
 * All rights reserved
 *
 * $Id: patricia.c,v 1.1.1.1 2000/11/06 19:53:17 mguthaus Exp $
 */

#include <stdlib.h>	/* free(), malloc() */
#include <string.h>	/* memmove() */



/*
 * Private function used to return whether
 * or not bit 'i' is set in 'key'.
 */
static __inline
unsigned long
bit(int i, unsigned long key)
{
	return key & (1 << (31-i));
}


/*
 * Count the number of masks (and therefore entries)
 * in the Patricia trie.
 */
static int
pat_count(struct ptree *t, int b)
{
	int count;
	
	if (t->p_b <= b) return 0;

	count = t->p_mlen;
	
	count += pat_count(t->p_left,  t->p_b);
	count += pat_count(t->p_right, t->p_b);

	return count;
}


/*
 * Private function used for inserting a node recursively.
 */
static struct ptree *
insertR(struct ptree *h, struct ptree *n, int d, struct ptree *p)
{
	if ((h->p_b >= d) || (h->p_b <= p->p_b)) {
		n->p_b = d;
		n->p_left = bit(d, n->p_key) ? h : n;
		n->p_right = bit(d, n->p_key) ? n : h;
		return n;
	}

	if (bit(h->p_b, n->p_key))
		h->p_right = insertR(h->p_right, n, d, h);
	else
		h->p_left = insertR(h->p_left, n, d, h);
	return h;
}


/*
 * Patricia trie insert.
 *
 * 1) Go down to leaf.
 * 2) Determine longest prefix match with leaf node.
 * 3) Insert new internal node at appropriate location and
 *    attach new external node.
 */
struct ptree *
pat_insert(struct ptree *n, struct ptree *head)
{
	struct ptree *t;
	struct ptree_mask *buf, *pm;
	int i, copied;

	if (!head || !n || !n->p_m)
		return 0;

	/*
	 * Make sure the key matches the mask.
	 */
	n->p_key &= n->p_m->pm_mask;

	/*
	 * Find closest matching leaf node.
	 */
	t = head;
	do {
		i = t->p_b;
		t = bit(t->p_b, n->p_key) ? t->p_right : t->p_left;
	} while (i < t->p_b);

	/*
	 * If the keys are the same we need to check the masks.
	 */
	if (n->p_key == t->p_key) {
		/*
		 * If we have a duplicate mask, replace the entry
		 * with the new one.
		 */
		for (i=0; i < t->p_mlen; i++) {
			if (n->p_m->pm_mask == t->p_m[i].pm_mask) {
				t->p_m[i].pm_data = n->p_m->pm_data;
				free(n->p_m);
				free(n);
				n = 0;
				return t;
			}
		}
		
		/*
		 * Allocate space for a new set of masks.
		 */
		buf = (struct ptree_mask *)malloc(
		       sizeof(struct ptree_mask)*(t->p_mlen+1));

		/*
		 * Insert the new mask in the proper order from least
		 * to greatest mask.
		 */
		copied = 0;
		for (i=0, pm=buf; i < t->p_mlen; pm++) {
			if (n->p_m->pm_mask > t->p_m[i].pm_mask) {
                            memmove(pm, t->p_m + i, sizeof(struct ptree_mask));
				i++;
			}
			else {
                            memmove(pm, n->p_m, sizeof(struct ptree_mask));
				n->p_m->pm_mask = 0xffffffff;
				copied = 1;
			}
		}
		if (!copied) {
                    memmove(pm, n->p_m, sizeof(struct ptree_mask));
		}
		free(n->p_m);
		free(n);
		n = 0;
		t->p_mlen++;

		/*
		 * Free old masks and point to new ones.
		 */
		free(t->p_m);
		t->p_m = buf;
		
		return t;
	}

	/*
	 * Find the first bit that differs.
	 */
	for (i=1; i < 32 && bit(i, n->p_key) == bit(i, t->p_key); i++); 

	/*
	 * Recursive step.
	 */
	if (bit(head->p_b, n->p_key))
		head->p_right = insertR(head->p_right, n, i, head);
	else
		head->p_left = insertR(head->p_left, n, i, head);
	
	return n;
}


/*
 * Remove an entry given a key in a Patricia trie.
 */
int
pat_remove(struct ptree *n, struct ptree *head)
{
	struct ptree *p, *g, *pt, *pp, *t;
	struct ptree_mask *buf, *pm;
	int i;

	if (!n || !n->p_m || !t)
		return 0;

	/*
	 * Search for the target node, while keeping track of the
	 * parent and grandparent nodes.
	 */
	g = p = t = head;
	do {
		i = t->p_b;
		g = p;
		p = t;
		t = bit(t->p_b, n->p_key) ? t->p_right : t->p_left;
	} while (i < t->p_b);

	/*
	 * For removal, we need an exact match.
	 */
	if (t->p_key != n->p_key)
		return 0;

	/*
	 * If there is only 1 mask, we can remove the entire node.
	 */
	if (t->p_mlen == 1) {
		/*
		 * Don't allow removal of the default entry.
		 */
		if (t->p_b == 0)
			return 0;
		
		/*
		 * Must match on the mask.
		 */
		if (t->p_m->pm_mask != n->p_m->pm_mask)
			return 0;
		
		/*
		 * Search for the node that points to the parent, so
		 * we can make sure it doesn't get lost.
		 */
		pp = pt = p;
		do {
			i = pt->p_b;
			pp = pt;
			pt = bit(pt->p_b, p->p_key) ? pt->p_right : pt->p_left;
		} while (i < pt->p_b);

		if (bit(pp->p_b, p->p_key))
			pp->p_right = t;
		else
			pp->p_left = t;

		/*
		 * Point the grandparent to the proper node.
		 */
		if (bit(g->p_b, n->p_key))
			g->p_right = bit(p->p_b, n->p_key) ?
				p->p_left : p->p_right;
		else
			g->p_left = bit(p->p_b, n->p_key) ?
				p->p_left : p->p_right;
	
		/*
		 * Delete the target's data and copy in its parent's
		 * data, but not the bit value.
		 */
		if (t->p_m->pm_data)
			free(t->p_m->pm_data);
		free(t->p_m);
		if (t != p) {
			t->p_key = p->p_key;
			t->p_m = p->p_m;
			t->p_mlen = p->p_mlen;
		}
		free(p);

		return 1;
	}

	/*
	 * Multiple masks, so we need to find the one to remove.
	 * Return if we don't match on any of them.
	 */
	for (i=0; i < t->p_mlen; i++)
		if (n->p_m->pm_mask == t->p_m[i].pm_mask)
			break;
	if (i >= t->p_mlen)
		return 0;
	
	/*
	 * Allocate space for a new set of masks.
	 */
	buf = (struct ptree_mask *)malloc(
	       sizeof(struct ptree_mask)*(t->p_mlen-1));

	for (i=0, pm=buf; i < t->p_mlen; i++) {
		if (n->p_m->pm_mask != t->p_m[i].pm_mask) {
                    memmove(pm++, t->p_m + i, sizeof(struct ptree_mask));
		}
	}
		
	/*
	 * Free old masks and point to new ones.
	 */
	t->p_mlen--;
	free(t->p_m);
	t->p_m = buf;
	return 1;
}


/*
 * Find an entry given a key in a Patricia trie.
 */
struct ptree *
pat_search(unsigned long key, struct ptree *head)
{
	struct ptree *p = 0, *t = head;
	int i;
	
	if (!t)
		return 0;

	/*
	 * Find closest matching leaf node.
	 */
	do {
		/*
		 * Keep track of most complete match so far.
		 */
		if (t->p_key == (key & t->p_m->pm_mask)) {
			p = t;
		}
		
		i = t->p_b;
		t = bit(t->p_b, key) ? t->p_right : t->p_left;
	} while (i < t->p_b);

	/*
	 * Compare keys (and masks) to see if this
	 * is really the node we want.
	 */
	return (t->p_key == (key & t->p_m->pm_mask)) ? t : p;
}

/* Inlined source patricia_test.c */
/*
 * patricia_test.c
 *
 * Patricia trie test code.
 *
 * This code is an example of how to use the Patricia trie library for
 * doing longest-prefix matching.  We begin by adding a default
 * route/default node as the head of the Patricia trie.  This will become
 * an initialization functin (pat_init) in the future.  We then read in a
 * set of IPv4 addresses and network masks from "pat_test.txt" and insert
 * them into the Patricia trie.  I haven't _yet_ added example of searching
 * and removing nodes.
 *
 * Compiling the library:
 *     gcc -g -Wall -c patricia.c
 *     ar -r libpatricia.a patricia.o
 *     ranlib libpatricia.a
 *
 * Compiling the test code (or any other file using libpatricia):
 *     gcc -g -Wall -I. -L. -o ptest patricia_test.c -lpatricia
 *
 * Matthew Smart <mcsmart@eecs.umich.edu>
 *
 * Copyright (c) 2000
 * The Regents of the University of Michigan
 * All rights reserved
 *
 * $Id: patricia_test.c,v 1.1.1.1 2000/11/06 19:53:17 mguthaus Exp $
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* #include <endian.h> FGG commented for portability */



/* 
#if !defined(BYTE_ORDER) || !defined(LITTLE_ENDIAN) || !defined(BIG_ENDIAN)
#error Cannot determine endianness
#endif
*/

/*#if BYTE_ORDER == LITTLE_ENDIAN */
/* Assuming little endian architecture */
#define bswap32(x) \
     ((((x) & 0xff000000) >> 24) | (((x) & 0x00ff0000) >>  8) | \
      (((x) & 0x0000ff00) <<  8) | (((x) & 0x000000ff) << 24))
#define htonl bswap32
/* #elif BYTE_ORDER == BIG_ENDIAN */
/* Assuming big endian architecture */
/* #define htonl(x) x
#else
#error Unsupported endianness
#endif */

typedef unsigned int in_addr_t;
struct in_addr {
    in_addr_t s_addr;
};

struct MyNode {
	int foo;
	double bar;
};

int
main1(int argc, char **argv, int print)
{
	struct ptree *phead;
	struct ptree *p,*pfind;
	struct ptree_mask *pm;
	FILE *fp;
	char line[128];
	char addr_str[16];
	struct in_addr addr;
	unsigned long mask=0xffffffff;
	float time;

	if (argc<2) {
		printf("Usage: %s <TCP stream>\n", argv[0]);
		exit(EXIT_FAILURE);
	}
	/*
	 * Open file of IP addresses and masks.
	 * Each line looks like:
	 *    10.0.3.4 0xffff0000
	 */
	if ((fp = fopen(argv[1], "r")) == NULL) {
		printf("File %s doesn't seem to exist\n",argv[1]);
		exit(EXIT_FAILURE);
	}

	/*
	 * Initialize the Patricia trie by doing the following:
	 *   1. Assign the head pointer a default route/default node
	 *   2. Give it an address of 0.0.0.0 and a mask of 0x00000000
	 *      (matches everything)
	 *   3. Set the bit position (p_b) to 0.
	 *   4. Set the number of masks to 1 (the default one).
	 *   5. Point the head's 'left' and 'right' pointers to itself.
	 * NOTE: This should go into an intialization function.
	 */
	phead = (struct ptree *)malloc(sizeof(struct ptree));
	if (!phead) {
		perror("Allocating p-trie node");
		exit(EXIT_FAILURE);
	}
	memset(phead, 0, sizeof(*phead));
	phead->p_m = (struct ptree_mask *)malloc(
			sizeof(struct ptree_mask));
	if (!phead->p_m) {
		perror("Allocating p-trie mask data");
		exit(EXIT_FAILURE);
	}
	memset(phead->p_m, 0, sizeof(*phead->p_m));
	pm = phead->p_m;
	pm->pm_data = (struct MyNode *)malloc(sizeof(struct MyNode));
	if (!pm->pm_data) {
		perror("Allocating p-trie mask's node data");
		exit(EXIT_FAILURE);
	}
	memset(pm->pm_data, 0, sizeof(*pm->pm_data));
	/*******
	 *
	 * Fill in default route/default node data here.
	 *
	 *******/
	phead->p_mlen = 1;
	phead->p_left = phead->p_right = phead;


	/*
	 * The main loop to insert nodes.
	 */
	while (fgets(line, 128, fp)) {
		/*
		 * Read in each IP address and mask and convert them to
		 * more usable formats.
		 */
		sscanf(line, "%f %d", &time, (unsigned int *)&addr);
		//inet_aton(addr_str, &addr);

		/*
		 * Create a Patricia trie node to insert.
		 */
		p = (struct ptree *)malloc(sizeof(struct ptree));
		if (!p) {
			perror("Allocating p-trie node");
			exit(EXIT_FAILURE);
		}
		memset(p, 0, sizeof(*p));

		/*
		 * Allocate the mask data.
		 */
		p->p_m = (struct ptree_mask *)malloc(
				sizeof(struct ptree_mask));
		if (!p->p_m) {
			perror("Allocating p-trie mask data");
			exit(EXIT_FAILURE);
		}
		memset(p->p_m, 0, sizeof(*p->p_m));

		/*
		 * Allocate the data for this node.
		 * Replace 'struct MyNode' with whatever you'd like.
		 */
		pm = p->p_m;
		pm->pm_data = (struct MyNode *)malloc(sizeof(struct MyNode));
		if (!pm->pm_data) {
			perror("Allocating p-trie mask's node data");
			exit(EXIT_FAILURE);
		}
		memset(pm->pm_data, 0, sizeof(*pm->pm_data));

		/*
		 * Assign a value to the IP address and mask field for this
		 * node.
		 */
		p->p_key = addr.s_addr;		/* Network-byte order */
		p->p_m->pm_mask = htonl(mask);

		pfind=pat_search(addr.s_addr,phead);
		//printf("%08x %08x %08x\n",p->p_key, addr.s_addr, p->p_m->pm_mask);
		//if(pfind->p_key==(addr.s_addr&pfind->p_m->pm_mask))
		if ((pfind->p_key==addr.s_addr) && (print==1))
		{
			printf("%f %08x: ", time, addr.s_addr);
			printf("Found.\n");
		}
		else
		{
			/*
		 	* Insert the node.
		 	* Returns the node it inserted on success, 0 on failure.
		 	*/
			//printf("%08x: ", addr.s_addr);
			//printf("Inserted.\n");
			p = pat_insert(p, phead);
		}
		if (!p) {
			fprintf(stderr, "Failed on pat_insert\n");
			exit(EXIT_FAILURE);
		}
	}

        fclose(fp);

        return 0; 
}

/* Main file ctuning-rtl.c */
/*
#
# Collective Tuning Run-Time
# Part of Collective Mind
#
# See cM LICENSE.txt for licensing details.
# See cM Copyright.txt for copyright details.
#
# Developer(s): (C) Grigori Fursin, started on 2011.09
#
*/

#include <stdio.h>
#include <stdlib.h>

#ifdef OPENME
#include <openme.h>
#endif
#ifdef XOPENME
#include <xopenme.h>
#endif

int main1(int argc, char* argv[], int print);

int main(int argc, char* argv[])
{
  long ct_repeat=0;
  long ct_repeat_max=1;
  int ct_return=0;
  int print=1;

#ifdef OPENME
  openme_init(NULL,NULL,NULL,0);
  openme_callback("PROGRAM_START", NULL);
#endif
#ifdef XOPENME
  xopenme_init(1,0);
#endif

  if (getenv("CT_REPEAT_MAIN")!=NULL) ct_repeat_max=atol(getenv("CT_REPEAT_MAIN"));
  			  
#ifdef OPENME
  openme_callback("KERNEL_START", NULL);
#endif
#ifdef XOPENME
  xopenme_clock_start(0);
#endif
  for (ct_repeat=0; ct_repeat<ct_repeat_max; ct_repeat++)
  {
    ct_return=main1(argc, argv, print);
    print=0;
  }
#ifdef XOPENME
  xopenme_clock_end(0);
#endif
#ifdef OPENME
  openme_callback("KERNEL_END", NULL);
#endif

#ifdef XOPENME
  xopenme_dump_state();
  xopenme_finish();
#endif
#ifdef OPENME
  openme_callback("PROGRAM_END", NULL);
#endif

  return ct_return;
}
