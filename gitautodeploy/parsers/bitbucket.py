from common import WebhookRequestParser

class BitBucketRequestParser(WebhookRequestParser):

    def get_repo_params_from_request(self, request_headers, request_body):
        import json
        import logging

        logger = logging.getLogger()
        data = json.loads(request_body)

        repo_urls = []
        ref = ""
        action = ""

        logger.debug("Received event from BitBucket")

        if 'repository' not in data:
            logger.error("Unable to recognize data format")
            return [], ref or "master", action

        # One repository may posses multiple URLs for different protocols
        for k in ['url', 'git_url', 'clone_url', 'ssh_url']:
            if k in data['repository']:
                repo_urls.append(data['repository'][k])

        if 'full_name' in data['repository']:
            repo_urls.append('git@bitbucket.org:%s.git' % data['repository']['full_name'])

            # Add a simplified version of the bitbucket HTTPS URL - without the username@bitbucket.com part. This is
            # needed since the configured repositories might be configured using a different username.
            repo_urls.append('https://bitbucket.org/%s.git' % (data['repository']['full_name']))

        # Get a list of configured repositories that matches the incoming web hook reqeust
        repo_configs = self.get_matching_repo_configs(repo_urls)

        return repo_configs, ref or "master", action, repo_urls